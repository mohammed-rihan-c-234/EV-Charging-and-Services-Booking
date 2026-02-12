from decimal import Decimal
from django.contrib.auth.models import User
from .models import RewardAccount


def award_points(user: User, amount: Decimal, description: str = ""):
    """
    Award reward points based on purchase amount.
    Points are awarded by spend thresholds.
    """
    if not isinstance(amount, Decimal):
        amount = Decimal(str(amount))

    points_to_award = 0
    if amount > Decimal("1000"):
        points_to_award = 150
    elif amount > Decimal("500"):
        points_to_award = 80
    elif amount > Decimal("200"):
        points_to_award = 40

    if points_to_award > 0:
        reward_account, created = RewardAccount.objects.get_or_create(user=user)
        reward_account.points += points_to_award
        reward_account.save(update_fields=["points"])

        return points_to_award

    return 0
