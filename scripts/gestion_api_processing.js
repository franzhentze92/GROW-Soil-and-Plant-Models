// list-paddocks server response
// let res = {
//     'status': 'success',
//     'data': [{
//         'id': 32,
//         'Farm_ID': '01jt95y93epm5sf3jeb79wkwp2',
//         'FarmName': 'Farm Name',
//         'FarmOwner_Id': '360',
//         'BusinessName': 'Business Name',
//         'FarmDescription': 'Farm Description',
//         'Picture': '01jt95y93epm5sf3jeb79wkwp2.jpg',
//         'PictureFilePath': 'public\\images\\FarmImages\\01jt95y93epm5sf3jeb79wkwp2.jpg',
//         'Area': 2000,
//         'AreaUnit': 'daa',
//         'Address': 'address',
//         'City': 'city',
//         'ZipCode': '10000',
//         'Country': 'United States',
//         'CreatedBy': 'bitnami22',
//         'created_at': '2025-05-02T19:00:30.000000Z',
//         'updated_at': '2025-05-02T19:00:30.000000Z'}],
//     'data1': [{
//         'id': 35,
//         'Farm_ID': '01jt95y93epm5sf3jeb79wkwp2',
//         'Paddock_ID': '01jt960dap7sg1hzqhevcmj9zk',
//         'PaddockName': 'paddock name',
//         'Area': null,
//         'AreaUnit': null,
//         'CropType': 'Alfalfa for seed',
//         'Variety': 'crop variety',
//         'PlantingDate': null,
//         'DistanceBetweenPlants': null,
//         'DistanceBetweenRows': null,
//         'PlantSupplier': null,
//         'TotalPlants': null,
//         'PaddockLocation': '{"type":"FeatureCollection","features":[{"id":"63e910a94d10c3fd00238e2229e793dc","type":"Feature","properties":{},"geometry":{"coordinates":[[[-91.90219765649569,42.77596875836292],[-91.82912127077462,42.7769768086398],[-91.82979175632835,42.72456805123633],[-91.90838525811111,42.72454027682542],[-91.92278394233718,42.7502774913828],[-91.90219765649569,42.77596875836292]]],"type":"Polygon"}}],"center":"-91.89760052809254,42.756223078760456","zoom":11}',
//         'CreatedBy': 'bitnami22',
//         'created_at': '2025-05-02T19:01:40.000000Z',
//         'updated_at': '2025-05-02T19:01:40.000000Z'}],
//     'map': 'false',
//     'user': {
//     'id': 360,
//         'name': 'bitnami22',
//         'email': 'bitnami222@mail.com',
//         'email_verified_at': null,
//         'created_at': '2025-04-09T22:17:27.000000Z',
//         'updated_at': '2025-05-12T10:48:01.000000Z',
//         'Role': 'FarmOwner',
//         'username': 'bitnami222',
//         'phone_number': '0110911191',
//         'profile_picture': '/profile_pictures/1744237047_440917.jpg',
//         'address': 'address\r\ncity',
//         'currency_name': 'US Dollar',
//         'currency_sign': '$',
//         'register_via': 'manual',
//         'onboarding_show': 0}
//     };

import fetch from 'node-fetch';

const body  = {"token": "7|XBodoDMpcDCuAtjDtlAWM78e60N1rw7mwiDyuDrH609149e9"};
const url   = 'http://localhost:8000/api/farm-management/list-paddocks';

fetch(url, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify(body)
})
.then(response => response.json())
.then(res => {
    // Check if the response is successful
    if (res.status === 'success') {        
        let farmsData = {};
        // const farmsData = {
        //     "Farm A": ["Paddock A1", "Paddock A2"],
        //     "Farm B": ["Paddock B1", "Paddock B2", "Paddock B3"]
        // };
        
        // Iterate through all of the paddocks
        for (let i = 0; i < res.data1.length; i++) {
            const paddock = res.data1[i];

            const paddock__Name     = paddock.PaddockName;
            const paddock__Farm_ID  = paddock.Farm_ID;
            const farm__farmName    = res.data.filter(farm => farm.Farm_ID === paddock__Farm_ID)[0].FarmName;

            // Check if the farm already exists in the farmsData object
            if (!farmsData[farm__farmName]) {
                farmsData[farm__farmName] = [];
            }

            // Add the paddock to the farm's array
            farmsData[farm__farmName].push(paddock__Name);
        }

        console.log(farmsData);
    } else {
        console.error('Error fetching data:', res);
    }
})

