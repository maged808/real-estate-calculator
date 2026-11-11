"""Pure calculation logic for the MAGED REAL ESTATE CALCULATOR.

All math uses decimal.Decimal so results are exact (no floating-point drift).
Values are rounded to 2 decimals (half-up) only at the final output step.
"""

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

CENT = Decimal("0.01")
HUNDRED = Decimal("100")

# Arabic-Indic / Persian digits and separators -> ASCII
_TRANSLATION = str.maketrans(
    {
        **{chr(0x0660 + i): str(i) for i in range(10)},  # ٠١٢٣٤٥٦٧٨٩
        **{chr(0x06F0 + i): str(i) for i in range(10)},  # ۰۱۲۳۴۵۶۷۸۹
        "٫": ".",  # Arabic decimal separator
        "٬": "",   # Arabic thousands separator
        "،": "",   # Arabic comma
        ",": "",
        " ": "",
        "\u00a0": "",
    }
)


def _round(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def to_decimal(value) -> Decimal:
    """Convert int / float / str / Decimal to Decimal safely."""
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError(f"قيمة غير صالحة: {value!r}") from exc


def parse_amount(text: str):
    """Parse a user-typed amount (supports Arabic digits and separators).

    Returns None for empty input. Raises ValueError for invalid or negative input.
    """
    cleaned = (text or "").strip().translate(_TRANSLATION)
    if cleaned == "":
        return None
    try:
        amount = Decimal(cleaned)
    except InvalidOperation as exc:
        raise ValueError("برجاء إدخال أرقام فقط.") from exc
    if not amount.is_finite():
        raise ValueError("برجاء إدخال رقم صحيح.")
    if amount < 0:
        raise ValueError("لا يمكن إدخال قيمة سالبة.")
    return amount


@dataclass(frozen=True)
class InstallmentResult:
    unit_price: Decimal            # original price
    discount_pct: Decimal
    discount_amount: Decimal
    price_after_discount: Decimal
    down_pct: Decimal
    down_payment: Decimal
    remaining: Decimal
    years: Decimal
    annual: Decimal
    quarterly: Decimal
    monthly: Decimal


def calculate(unit_price, down_pct, years, discount_pct=0) -> InstallmentResult:
    """Compute the installment plan.

    Order of operations (as required):
      1. Apply discount to the unit price.
      2. Down payment = discounted price x down% / 100.
      3. Remaining   = discounted price - down payment.
      4. Annual      = remaining / years.
      5. Quarterly   = annual / 4.   Monthly = annual / 12.
    """
    price = to_decimal(unit_price)
    down = to_decimal(down_pct)
    n_years = to_decimal(years)
    disc = to_decimal(discount_pct)

    if price < 0:
        raise ValueError("سعر الوحدة لا يمكن أن يكون سالبًا.")
    if not (Decimal(0) <= down <= HUNDRED):
        raise ValueError("نسبة المقدم يجب أن تكون بين 0 و 100.")
    if not (Decimal(0) <= disc <= HUNDRED):
        raise ValueError("نسبة الخصم يجب أن تكون بين 0 و 100.")
    if n_years <= 0:
        raise ValueError("عدد سنوات التقسيط يجب أن يكون أكبر من صفر.")

    discount_amount = price * disc / HUNDRED
    net_price = price - discount_amount
    down_payment = net_price * down / HUNDRED
    remaining = net_price - down_payment
    annual = remaining / n_years
    quarterly = annual / 4
    monthly = annual / 12

    return InstallmentResult(
        unit_price=_round(price),
        discount_pct=disc,
        discount_amount=_round(discount_amount),
        price_after_discount=_round(net_price),
        down_pct=down,
        down_payment=_round(down_payment),
        remaining=_round(remaining),
        years=n_years,
        annual=_round(annual),
        quarterly=_round(quarterly),
        monthly=_round(monthly),
    )


def fmt_money(value: Decimal) -> str:
    """12345.6 -> '12,345.60'"""
    return f"{value:,.2f}"


def fmt_number(value: Decimal) -> str:
    """Strip trailing zeros: 5.0 -> '5', 12.50 -> '12.5'"""
    text = f"{value.normalize():f}"
    return text


def build_message(r: InstallmentResult) -> str:
    """Formatted Arabic message with all results, ready to copy."""
    lines = [
        "🏢 MAGED REAL ESTATE CALCULATOR",
        "حاسبة التقسيط العقاري",
        "━━━━━━━━━━━━━━━",
        f"💰 سعر الوحدة: {fmt_money(r.unit_price)} جنيه",
    ]
    if r.discount_pct > 0:
        lines += [
            f"🏷️ نسبة الخصم: {fmt_number(r.discount_pct)}%",
            f"➖ قيمة الخصم: {fmt_money(r.discount_amount)} جنيه",
            f"✅ السعر بعد الخصم: {fmt_money(r.price_after_discount)} جنيه",
        ]
    lines += [
        "━━━━━━━━━━━━━━━",
        f"💵 المقدم ({fmt_number(r.down_pct)}%): {fmt_money(r.down_payment)} جنيه",
        f"📉 المبلغ المتبقي: {fmt_money(r.remaining)} جنيه",
        f"📅 مدة التقسيط: {fmt_number(r.years)} سنة",
        "━━━━━━━━━━━━━━━",
        f"🗓️ القسط السنوي: {fmt_money(r.annual)} جنيه",
        f"📆 القسط الربع سنوي: {fmt_money(r.quarterly)} جنيه",
        f"🧾 القسط الشهري: {fmt_money(r.monthly)} جنيه",
        "━━━━━━━━━━━━━━━",
        "جميع المبالغ بالجنيه المصري (EGP)",
    ]
    return "\n".join(lines)
