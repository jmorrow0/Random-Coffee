import csv
import random
import sys


class participant:
    def __init__(self, id, email, name, previous_matches):
        self.id = id
        self.name = name
        self.email = email
        self.previous_matches = previous_matches
        self.names = name.split()
        self.first_name = self.names[0]  #Assumes given name first
        self.matching = True
        self.new_match = None

    def valid_match(self, other):
        return (other not in self.previous_matches) and (other != self.id)

    def __repr__(self):
        return str(self.id) + ', ' + str(self.name) + ', ' + str(self.email)

    def __str__(self):
        return '(' + str(self.name) + ', ' + str(self.email) + ', ' + str(self.id) + ')'


class pool:
    def __init__(self):
        self.participants = dict()
        self.not_matching = []

    def not_matching_from_file(self, filename='month_skip.csv'):
        with open(filename, encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if row != []:
                    self.not_matching.append(int(row[2]))

    def get_participant_info(self, filename='match_history.csv'):
        with open(filename, encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                self.participants[int(row[2])] = participant(int(row[2]), row[1], row[0],
                                                             [int(x) for x in row[3:] if x != ''])
                if int(row[2]) in self.not_matching:
                    self.participants[int(row[2])].matching = False

    def run_matching(self, email_text, current_match_filename = 'current_matches.csv',
                     formatted_matches_filename='formatted match.csv'):
        participants = list(self.participants.keys())
        matching_pool = [x for x in participants if self.participants[x].matching]
        ticks = 0
        while len(matching_pool) > 1:
            p1 = random.choice(matching_pool)
            p2 = random.choice(matching_pool)
            if self.participants[p1].valid_match(p2) and self.participants[p2].valid_match(p1):
                self.participants[p1].new_match = p2
                self.participants[p2].new_match = p1
                matching_pool = [x for x in matching_pool if x not in {p1, p2}]
            ticks += 1
            if ticks > 1000:
                print(matching_pool)
                sys.exit()

        if len(matching_pool) > 1:
            print('Error: too few matches made')
        if len(matching_pool) == 1:
            print('Matching pool is odd. The following participant has not matched:')
            print([self.participants[matching_pool[0]], 0 in self.participants[matching_pool[0]].previous_matches])

        participant_list = list(self.participants.keys())
        participant_list.sort()

        with open(current_match_filename, mode='w', newline='\n', encoding='utf-8') as current_match_file:
            with open(formatted_matches_filename, mode='w', newline='\n', encoding='utf-8') as formatted_match_file:
                current_match_writer = csv.writer(current_match_file)

                formatted_match_writer = csv.writer(formatted_match_file)

                matches_made = set()

                for part in participant_list:
                    if self.participants[part].new_match == None:
                        formatted_match_writer.writerow([part, ''])
                    else:
                        formatted_match_writer.writerow([part, self.participants[part].new_match])
                        if part not in matches_made:
                            p1 = self.participants[part]
                            p2 = self.participants[self.participants[part].new_match]
                            matches_made.add(p1.id)
                            matches_made.add(p2.id)
                            current_match_writer.writerow(
                                [p1.id, p2.id, p1.email + ',' + p2.email, 'Random Coffee Pairing',
                                 'Hi ' + p1.first_name + ' and ' + p2.first_name + ',\n\n' + email_text])


with open('email_text.txt') as f:
    email_text = f.read()

this_month = pool()

this_month.not_matching_from_file()
this_month.get_participant_info()

this_month.run_matching(email_text)
