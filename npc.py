import argparse
import Peing
import csv

argparse = argparse.ArgumentParser()
argparse.add_argument("user")
args = argparse.parse_args()
peing = Peing.Peing(args.user)
info = peing.get_user_info()
print("item count is %d", (info["answers_count"]))
answers = peing.get_user_answers(info["answers_count"])
with open("%s_answers.csv" % (peing.id), "w", newline="") as f:
	answer_csv = csv.writer(f)
	answer_csv.writerow(("質問", "回答"))
	for q, a in answers.items():
		answer_csv.writerow((q, a))
print("Done!")
