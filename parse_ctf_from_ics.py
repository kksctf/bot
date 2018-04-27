from datetime import datetime


def parse_ctf_from_ics(s):

    f = s.split('\n')
    a = dict()

    for line in f:
        if 'DESCRIPTION' in line:
            a['name'] = line.split(':')[1]
            
        if 'URL' in line:
            a['link'] = line.split('URL:')[1]
            
        if 'SUMMARY' in line:
            if 'Jeopardy' in line:
                a['type'] = 'Jeopardy'
            elif 'Attack-Defense' in line:
                a['type'] = 'Attack-Defense'
            else:
                a['type'] = 'Without category'
                
        if 'DTSTART' in line:
            data_s = line[8:21]
            point_s = datetime.strptime(f'{data_s}', '%Y%m%dT%H%M')
            start = int(point_s.timestamp())
            a['start'] = start
            
        if 'DTEND' in line:
            data_e = line[6:19]
            point_e = datetime.strptime(f'{data_e}', '%Y%m%dT%H%M')
            end = int(point_e.timestamp())
            duration = int((end - start) / 3600)
            a['duration'] = duration
            
    return a


if __name__ == '__main__':
    parse_ctf_from_ics(s)
