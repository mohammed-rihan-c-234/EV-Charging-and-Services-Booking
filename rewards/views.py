from django.shortcuts import render
from .models import RewardAccount
from django.http import JsonResponse
from .models import Coupon


def rewards_list(request):
    accounts = RewardAccount.objects.select_related('user').all()
    coupons = Coupon.objects.filter(active=True).order_by('-discount_percent', 'code')
    
    # Get current user's points
    total_points = 0
    if request.user.is_authenticated:
        try:
            reward_account = RewardAccount.objects.get(user=request.user)
            total_points = reward_account.points
        except RewardAccount.DoesNotExist:
            total_points = 0
    
    return render(request, 'rewards/rewards_list.html', {
        'accounts': accounts, 
        'coupons': coupons,
        'total_points': total_points
    })


def api_my_rewards(request):
    """Return the current user's reward balance as JSON. Requires authentication."""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'authentication required'}, status=401)

    try:
        acct = RewardAccount.objects.get(user=request.user)
    except RewardAccount.DoesNotExist:
        return JsonResponse({'points': 0, 'redeemable': 0})

    return JsonResponse({'points': acct.points, 'redeemable': getattr(acct, 'redeemable_points', 0)})
