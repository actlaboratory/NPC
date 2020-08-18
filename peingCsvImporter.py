import winsound
import argparse
import peing
import csv
import io

argparse = argparse.ArgumentParser()
argparse.add_argument("user")
args = argparse.parse_args()
user_id = args.user
answers = peing.getAnswers(user_id)
with open("%s_answers.csv" % (user_id), "wb") as f:
	csvf = io.StringIO()
	answer_csv = csv.writer(csvf)
	answer_csv.writerow(("質問", "回答", "日時"))
	for answer in answers:
		answer_csv.writerow((answer["body"], answer["answer_body"], answer["answer_created_at"]))
	bin = csvf.getvalue().encode("CP932", "replace")
	csvf.close()
	f.write(bin)
winsound.Beep(1900, 300)
print("Done!")
