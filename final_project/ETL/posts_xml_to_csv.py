#covnerting posts.xml to posts.csv
import xml.etree.ElementTree as Xet
import pandas as pd

cols = ["Id", "PostTypeId", "CreationDate", "Score", "ViewCount", "Body", "OwnerUserId", "LastActivityDate", "Title", "Tags", "AnswerCount", "CommentCount", "AcceptedAnswerId", "LastEditorUserId", "ParentId"]
rows = []

xmlparse = Xet.parse('C:\\Users\\Dell\\OneDrive - Northeastern University\\courses\\big data and intl analytics\\DAMG7245-Summer2023\\final project\\dataset\\3dprinting.stackexchange.com\\Posts.xml')
root = xmlparse.getroot()

for i in root:
    Id = int(i.get("Id"))
    PostTypeId = int(i.get("PostTypeId"))
    CreationDate = i.get("CreationDate")
    Score = int(i.get("Score"))
    ViewCount = float(i.get("ViewCount")) if i.get("ViewCount") is not None else None
    Body = i.get("Body")
    OwnerUserId = float(i.get("OwnerUserId")) if i.get("OwnerUserId") is not None else None
    LastActivityDate = i.get("LastActivityDate")
    Title = i.get("Title")
    Tags = i.get("Tags")
    AnswerCount = float(i.get("AnswerCount")) if i.get("AnswerCount") is not None else None
    CommentCount = int(i.get("CommentCount"))
    AcceptedAnswerId = float(i.get("AcceptedAnswerId")) if i.get("AcceptedAnswerId") is not None else None
    LastEditorUserId = float(i.get("LastEditorUserId")) if i.get("LastEditorUserId") is not None else None
    ParentId = float(i.get("ParentId")) if i.get("ParentId") is not None else None
    
    rows.append({"Id": Id, "PostTypeId": PostTypeId, "CreationDate": CreationDate, "Score": Score, "ViewCount": ViewCount, "Body": Body, "OwnerUserId": OwnerUserId, "LastActivityDate": LastActivityDate, "Title": Title, "Tags": Tags, "AnswerCount": AnswerCount, "CommentCount": CommentCount, "AcceptedAnswerId": AcceptedAnswerId, "LastEditorUserId": LastEditorUserId, "ParentId": ParentId})

df = pd.DataFrame(rows, columns=cols)
df.to_csv('output.csv')
