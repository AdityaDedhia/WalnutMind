from .models import CollectionOrder, Resource
from django.db.models import Max
from django.utils import timezone
import plotly.express as px
import calendar


def storage_usage(User):
    bytes = 0

    resources = Resource.objects.filter(creator = User)
    for resource in resources:
        if resource.filelink:
            bytes += resource.filelink.size

    return bytes


def resource_collection_order(collection) -> int:
    existing_resources = CollectionOrder.objects.filter(collection = collection)

    if not existing_resources.exists():  # If no resources in collection initialise first item order to 1
        return 1
    else:
        current_max = existing_resources.aggregate(max_order=Max('order'))['max_order']
        return current_max + 1


def resource_collection_reorder(collection):
    existing_resources = CollectionOrder.objects.filter(collection = collection)
    if not existing_resources.exists():
        return
    resource_count = existing_resources.count()
    new_order = range(1, resource_count+1)

    for order, resource in zip(new_order, existing_resources):
        resource.order = order
        resource.save()


def date_range(start, end):
    delta = end - start
    dates = []
    for i in range(delta.days):
        dates.append(start + timezone.timedelta(days=i))
    return dates


def get_resource_heatmap(User):
    now = timezone.now() + timezone.timedelta(days=1)  # End date
    start = now - timezone.timedelta(days=182)  # Days must be exactly plottable in a nxn grid.

    daterange = date_range(start, now)

    # Create a list of lists, each list containing the number of resources created in each day
    counts = [[] for i in range(7)]
    dates = [[] for i in range(7)]

    items = list(Resource.objects.filter(creator=User).only('dateCreated').order_by('dateCreated'))
    added = []

    for dt in daterange:
        count = 0
        for item in items:
            if item not in added:
                if item.dateCreated.date() == dt.date():
                    count += 1
                    added.append(item)
        day = dt.weekday()
        counts[day].append(count)
        dates[day].append(dt)

    # Generate graph
    days_list = list(calendar.day_name)
    # init_day = daterange[1].weekday()
    # days = days_list[init_day:] + days_list[:init_day]
    fig = px.imshow(
        counts,
        labels=dict(x="Week Beginning",y="Week Day", color="Additions"),
        color_continuous_scale='brwnyl',
        x=dates[0],
        y=days_list,
        height=300,  # width is set by autosize attribute
    )
    fig.update_layout(
        plot_bgcolor='#ffffff',
        title = 'Your Activity Heatmap',
        autosize = True,
        )

    fig.update_traces(
        {'xgap': 5, 'ygap': 5},
        )

    chart = fig.to_html(
        config=dict(
            displayModeBar = False,
        ),
    )
    return chart
