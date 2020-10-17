def parse_hashtags(data):
    data = data.replace('#','')
    data = data.split(',')
    for d in data:
        d.replace(' ','')

    return data

def parse_profiles(data):
    data = data.split(',')
    for d in data:
        d.replace(' ', '')

    return data
