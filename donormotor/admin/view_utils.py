import datetime
import dateutil.parser
from donormotor import db
from donormotor.donate.models import Order

def donation_stats(startdate):
    stats = Order.query.with_entities(
        db.func.sum(Order.amount).label('total_paid'),
        db.func.max(Order.amount).label('max_paid'))

    donation_stats_start = startdate
    if donation_stats_start is not None:
        last_stats_reset = dateutil.parser.parse(donation_stats_start)
        stats = stats.filter(Order.placed_date > last_stats_reset)
    else:
        last_stats_reset = None

    stats = stats.all()

    total = stats[0][0]
    if total is None:
        total = 0

    max_donation = stats[0][1]
    if max_donation is None:
        max_donation = 0
    
    return { 'max_donation': max_donation, 'last_stats_reset': last_stats_reset, 'total': total }

