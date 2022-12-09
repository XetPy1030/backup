import requests

cookies = {
    'MoodleSession': 'm7c7rshomskjpo7pos90vve4qc',
    'MOODLEID1_': '%9E%13%C5%A0%E7'
}


def upload_file():
    url = 'https://moodle.alabuga.space/repository/repository_ajax.php?action=upload'
    file = open('hw.txt', 'rb')
    resp = requests.post(url, cookies=cookies, files={"file": file}, data={'sesskey': 'M2cJWk6ebf', 'repo_id': 5, 'filename': 'daw'})
    print(resp, resp.json())
    

upload_file()
"""
-----------------------------313143451439581817803527812678
Content-Disposition: form-data; name="repo_upload_file"; filename="hw.txt"
Content-Type: text/plain

https://github.com/XetPy1030/django42.git

-----------------------------313143451439581817803527812678
Content-Disposition: form-data; name="sesskey"

M2cJWk6ebf
-----------------------------313143451439581817803527812678
Content-Disposition: form-data; name="repo_id"

5
-----------------------------313143451439581817803527812678
Content-Disposition: form-data; name="itemid"

421625378
-----------------------------313143451439581817803527812678
Content-Disposition: form-data; name="author"

Askar Kovin
-----------------------------313143451439581817803527812678
Content-Disposition: form-data; name="savepath"

/
-----------------------------313143451439581817803527812678
Content-Disposition: form-data; name="title"

hw.txt
-----------------------------313143451439581817803527812678
Content-Disposition: form-data; name="ctx_id"

1532
-----------------------------313143451439581817803527812678--


"""