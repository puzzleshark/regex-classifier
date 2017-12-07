import re
import os
from jinja2 import Environment, PackageLoader, select_autoescape, FileSystemLoader
env = Environment(
    loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates'))
)


class LetterClassifier(object):

    def __init__(self, class_name):
        self.class_name = class_name
        self._regs = []
        self.bias = 0
        self._highlights = ['#ffb7b7', '#B2ABFF', '#fff2a8', '#a8d1ff', '#78e3a5']

    def add_reg(self, reg, score):
        """
        Add a regular expression
        :param reg: a regular expression object
        :param score: a number, positive indicating a positive association, and negative indicating a negative association
        :return: None
        """
        self._regs.append((reg, score))

    def score_letter(self, letter):
        score, matches = self._score_letter(letter)
        return score

    def _score_letter(self, letter):
        current_score = self.bias
        matches = []
        for reg, score in self._regs:
            match = re.search(reg, letter)
            if match:
                current_score += score
                matches.append((match, score))
        return current_score, matches

    def add_bias(self, score):
        self.bias = score

    def highlight_matches(self, letter):
        """
        Add HTML span elements for highlighting to matched text in letter
        :param letter: string object
        :return: string object with HTML elements
        """
        def replace_match(matchobj):
            return '<span style="background-color:{}">'.format(self._highlights[i % len(self._highlights)]) \
                   + matchobj.group(0) + '</span>'

        for i, reg in enumerate(self._regs):
                letter = re.subn(reg[0], replace_match, letter)[0]
        return letter

    def generate_report(self, patient_ids, letters, labels, output_folder='.'):
        failures = []
        for i, letter in enumerate(letters):
            label = labels[i]
            score, matches = self._score_letter(letter)
            if (score > 0) != label:
                failures.append({'patient_id':patient_ids[i], 'letter':letter, 'label':label, 'score':score, 'matches':matches, 'highlight_letter': self.highlight_matches})

        template = env.get_template('report.html')
        if not os.path.isdir(output_folder):
            os.mkdir(output_folder)
        else:
            # remove any previously generated reports in this folder
            for filename in os.listdir(output_folder):
                if re.match(r'failure[0-9]+\.html', filename):
                    os.remove(os.path.join(output_folder, filename))
        # generate the new report
        for i, failure in enumerate(failures):
            output = template.render(failures=failures, current_failure=failure)
            with open(os.path.join(output_folder, "failure{}.html".format(i+1)), "w") as fh:
                fh.write(output)
        # print out statistics
        print('Got {num_correct} out of {num_total} ({percent}%)'.format(
            num_correct=len(patient_ids)-len(failures),
            num_total=len(patient_ids),
            percent=((len(patient_ids)-len(failures))/len(patient_ids))*100
        ))


if __name__ == '__main__':
    test = LetterClassifier('excited')
    test.add_reg('excited', 5)
    test.add_reg('happy', 2)
    test.add_reg(r"can't\ssleep", 3)
    test.add_reg('sad', -5)

    #print(test.score_letter("I am so excited, I can't sleep!"))
    test.generate_report([45, 34], ['I am so excited, very excited', 'so unhappy'], [False, False])