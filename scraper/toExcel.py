from django.http import HttpResponse

from scraper.models import Users
import csv
import os

def csv_new(filename):
    DATA = [['ID', 'Username', 'Posts', 'Subscribed to you', 'Subscribed by you', 'Following',
             'Followers', 'Name', 'Descriprion', 'Picture', 'Email']]
    with open(filename, 'w') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        for line in DATA:
            writer.writerow(line)


def csv_writer(data, filename):
    if not os.path.isfile(filename) or os.stat(filename).st_size == 0:
        csv_new(filename)

    with open(filename, "a") as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        for line in data:
            writer.writerow(line)

def export_using_filters(email_only, subscribed, subscribe):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="ExportInstaScraper.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'Username', 'Posts', 'Subscribed to you', 'Subscribed by you', 'Following',
                     'Followers', 'Name', 'Descriprion', 'Picture', 'Email'])

    if email_only and subscribed and subscribe:
        users = Users.objects.exclude(email=' ', subscribed_on_your_profile=' ', you_subscribed= ' ')
    elif email_only and subscribed:
        users = Users.objects.exclude(email=' ', subscribed_on_your_profile=' ')
    elif email_only and subscribe:
        users = Users.objects.exclude(email=' ', you_subscribed= ' ')
    elif subscribed and subscribe:
        users = Users.objects.exclude(subscribed_on_your_profile=' ', you_subscribed= ' ')
    elif email_only:
        users = Users.objects.exclude(email=' ')
    elif subscribed:
        users = Users.objects.exclude(subscribed_on_your_profile=' ')
    elif subscribe:
        users = Users.objects.exclude(you_subscribed= ' ')
    else:
        users = Users.objects.all()

    for user in users:
        data =  [user.id, user.username, user.posts, user.subscribed_on_your_profile,
                  user.you_subscribed, user.following, user.followers, user.name,
                  user.description, user.picture, user.email]
        writer.writerow(data)

    return response


if __name__ == '__main__':
    export_using_filters(False, False, False)


