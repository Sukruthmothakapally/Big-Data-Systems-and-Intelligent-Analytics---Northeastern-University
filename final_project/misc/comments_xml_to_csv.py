#covnerting comments.xml to comments.csv
import xml.etree.ElementTree as Xet
import pandas as pd

cols = ["Id", "PostId", "Score", "Text", "CreationDate", "UserId", "ContentLicense"]
rows = []

xmlparse = Xet.parse('C:\\Users\\Dell\\OneDrive - Northeastern University\\courses\\big data and intl analytics\\DAMG7245-Summer2023\\final project\\dataset\\3dprinting.stackexchange.com\\Comments.xml')
root = xmlparse.getroot()

for i in root:
    Id = int(i.get("Id"))
    PostId = int(i.get("PostId"))
    Score = int(i.get("Score"))
    Text = i.get("Text")
    CreationDate = i.get("CreationDate")
    UserId = float(i.get("UserId")) if i.get("UserId") is not None else None
    ContentLicense = i.get("ContentLicense")
    
    rows.append({"Id": Id, "PostId": PostId, "Score": Score, "Text": Text, "CreationDate": CreationDate, "UserId": UserId, "ContentLicense": ContentLicense})
df = pd.DataFrame(rows, columns=cols)
df.to_csv('C:\\Users\\Dell\\OneDrive - Northeastern University\\courses\\big data and intl analytics\\DAMG7245-Summer2023\\final project\\dataset_converted\\3d_printing\\comments.csv')
