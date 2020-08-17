import winsound
import argparse
import Peing
import csv
import io

argparse = argparse.ArgumentParser()
argparse.add_argument("user")
args = argparse.parse_args()
peing = Peing.Peing(args.user)
info = peing.get_user_info()
print("item count is %s" % (info["answers_count"]))
answers = peing.get_user_answers(info["answers_count"])
with open("%s_answers.csv" % (peing.id), "wb") as f:
	csvf = io.StringIO()
	answer_csv = csv.writer(csvf)
	answer_csv.writerow(("質問", "回答"))
	for q, a in answers.items():
		answer_csv.writerow((q, a))
	bin = csvf.getvalue().encode("CP932", "replace")
	csvf.close()
	f.write(bin)
winsound.Beep(1900, 300)
print("Done!")
