# Service Discovery
### description:
* A project to set up three Orthanc DICOM servers.
* you can add as many servers as you want.
* a Python service discovery client.

![server count](https://github.com/user-attachments/assets/63dcb7be-fada-49c6-b40e-e2db7ed6269d)

**if any server goes down :**

![server updates](https://github.com/user-attachments/assets/06432e70-0eb2-4cba-8808-358513157f21)

**and after a few seconds :**
![server  down](https://github.com/user-attachments/assets/513c2f89-b61b-4594-9ee6-b25d10ba52c3)

### Structure:
```bash
.
├── discovery
│   ├── dashboard.html
│   ├── requirements.txt
│   └── service_discovery.py
├── docker-compose.yml
├── scripts
│   └── add_orthanc.sh
└── servers.json
```

### How it works:
* first three servers are live 
* the clients checks host ports and check if those ports are occupied by orthanc.
* then genarate a json file with info stats about these orthanc servers.
* then sends the json file to ```@app.route('/servers.json')``` route.
* javascript client fethces the data and using that data we create a buitiful dahsboard using bootstrap.
* notice that scraping and checking ports is done via a thread running in the background that rescans every 3 second to update the dashboard.
* if server goes down it gets noticed and the dashboard gets updated as the JS client fetches the json data every 2 seconds.

### how to run :
* run ```docker compose ip -d``` to have 3 Orthanc servers up
* create a virtualenv then activate it and then install requirements.txt ```pip install -r ./discovery/requirements.txt``` if you are at the root dir
* then run the flask app
* check the dashboard
* try to have one extra server using add_orthanc.sh file
* the dashboard gets updated
* try to have a django serveron a some port the dashboard doesn't update
* the discovery file only notices Orthanc servers
* try to stop one server ```docker stop orthanc2```
* the dashbooard gets updated

##### you can easilt Interact with those servers though their exposed REST API

### Next Steps :
* make the dashboard gets more insights about those servers through their REST API
* we can get data about DICOM data they have and more info [REST API Interaction](https://github.com/mahmoudnasser1561/DICOM?tab=readme-ov-file#uses-rest-api-queries-to-inspect-stored-dicom-instances-and-query-your-servers)
* we can get more servver metrics as we done [monitoring.log](https://github.com/mahmoudnasser1561/DICOM/blob/main/monitoring.log)
* those metrics could be used to build more features upon
