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
        current_score = 0
        matches = []
        for reg, score in self._regs:
            match = reg.search(letter)
            if match:
                current_score += score
                matches.append((match, score))
        return current_score, matches

    def generate_report(self, patient_ids, letters, labels, output_folder='.'):
        failures = []
        for i, letter in enumerate(letters):
            label = labels[i]
            score, matches = self._score_letter(letter)
            if (score > 0) != label:
                failures.append({'patient_id':patient_ids[i], 'letter':letter, 'label':label, 'score':score, 'matches':matches})

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


if __name__ == '__main__':
    test = LetterClassifier('excited')
    test.add_reg('excited', 5)
    test.add_reg('happy', 2)
    test.add_reg(r"can't\ssleep", 3)
    test.add_reg('sad', -5)

    #print(test.score_letter("I am so excited, I can't sleep!"))
    test.generate_report([45, 34], ['I am so excited', 'so unhappy'], [False, False])