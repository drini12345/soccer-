import requests
from datetime import date, datetime
from django.shortcuts import render
import pytz


def home(request):
    return render(request, 'blog/home.html')


def fetch_team_details(team_id, headers):
    api_url = f'http://api.football-data.org/v2/teams/{team_id}'
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch team details for team ID {team_id}. Status code: {response.status_code}")
        return None


def today_matches(request):
    today = date.today().isoformat()
    api_url = f'http://api.football-data.org/v2/matches?dateFrom={today}&dateTo={today}'
    headers = {'X-Auth-Token': 'b4514c7269ac429687a8f80cad6b9dfe'}

    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        match_data = response.json()
        matches = match_data.get('matches', [])

        for match in matches:
            home_team_id = match['homeTeam']['id']
            away_team_id = match['awayTeam']['id']

            home_team_details = fetch_team_details(home_team_id, headers)
            away_team_details = fetch_team_details(away_team_id, headers)

            match['homeTeam']['crest'] = home_team_details.get('crestUrl',
                                                               '/static/img/default_logo.png') if home_team_details else '/static/img/default_logo.png'
            match['awayTeam']['crest'] = away_team_details.get('crestUrl',
                                                               '/static/img/default_logo.png') if away_team_details else '/static/img/default_logo.png'

            # Parse and format the match time
            utc_date = match['utcDate']
            match_time = datetime.fromisoformat(utc_date.replace('Z', '+00:00'))
            local_time = match_time.astimezone(pytz.timezone('America/New_York'))  # Replace with your actual timezone
            match['formatted_time'] = local_time.strftime('%Y-%m-%d %H:%M')

        context = {'matches': matches, 'today': today}
        return render(request, 'blog/today_matches.html', context)
    else:
        error_message = f"Failed to fetch today's matches from the API. Status code: {response.status_code}"
        return render(request, 'blog/error.html', {'error': error_message})

