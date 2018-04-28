#!/usr/bin/env python3

from datetime import datetime
import ctftime_tools
import argparse
import json
import os


def parse_ctf_from_ics(s, id):
    """Return dict with info about ctf"""

    if s == "":
        return None

    f = s.split('\n')
    entry = dict(
        id=id,
        name='Unknown',
        link='example.com',
        ctftime_link=f'https://ctftime.org/event/{id}',
        type='Without category',
        start=0,
        duration=0
    )

    for line in f:
        if line.startswith('DESCRIPTION'):
            entry['name'] = line.split(':')[1]

        elif line.startswith('URL'):
            entry['link'] = line.split('URL:')[1]

        elif line.startswith('SUMMARY'):
            if 'Jeopardy' in line:
                entry['type'] = 'Jeopardy'
            elif 'Attack-Defense' in line:
                entry['type'] = 'Attack/Defense'
            else:
                entry['type'] = 'Without category'

        elif line.startswith('DTSTART'):
            data_s = line[8:21]
            point_s = datetime.strptime(f'{data_s}', '%Y%m%dT%H%M')
            start = int(point_s.timestamp())
            entry['start'] = start

        elif line.startswith('DTEND'):
            data_e = line[6:19]
            point_e = datetime.strptime(f'{data_e}', '%Y%m%dT%H%M')
            end = int(point_e.timestamp())
            duration = int((end - entry['start']) / 3600)
            entry['duration'] = duration

    return entry


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('calendar', type=str)
    parser.add_argument('id', type=str)

    args = parser.parse_args()

    if os.path.exists(args.calendar) and os.stat(args.calendar).st_size != 0:
        file_exists = True
    else:
        file_exists = False

    with open(args.calendar, "r+" if file_exists else "w+") as file:
        try:
            current = json.load(file)
            new = current
        except json.JSONDecodeError:
            new = dict()
            new['ctfs'] = list()

        new_entry = parse_ctf_from_ics(ctftime_tools.get_ctf_ics(args.id),
                                       args.id)
        if new_entry:
            if new_entry['id'] in [ i['id'] for i in new['ctfs'] ]:
                print(f"ID {new_entry['id']} already exist")
                return

            print(f"{new_entry['name']} added!")
            new['ctfs'].append(new_entry)
            file.seek(0)
            file.write(json.dumps(new, sort_keys=False, indent=2))


if __name__ == '__main__':
    main()
