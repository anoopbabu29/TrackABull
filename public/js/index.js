var config = {
    apiKey: "AIzaSyA4s65NGcz_9EfKiPmfFKmN9brXwYR7BcU",
    authDomain: "track-a-bull.firebaseapp.com",
    databaseURL: "https://track-a-bull.firebaseio.com",
    projectId: "track-a-bull",
    storageBucket: "track-a-bull.appspot.com",
    messagingSenderId: "819088197621"
};

firebase.initializeApp(config);

let itemsDb = firebase.database().ref('/Items/');
let fireFunct = firebase.functions();

function fillTable(ItemList) {
    let tbody = document.getElementById('itemTableBody');
    tbody.innerHTML = "";

    for(let i = 1; i < ItemList.length; i++){
        const idElem = document.createElement('td');
        const modelElem = document.createElement('td');
        const typeElem = document.createElement('td');
        const checkOutDateElem = document.createElement('td');
        const checkedOutByElem = document.createElement('td');

        const checkedOutBy = ItemList[i].CheckedOutBy ? ItemList[i].CheckedOutBy : "N/A";
        const checkOutDate = ItemList[i].CheckOutDate ? ItemList[i].CheckOutDate : "-";

        const idNode = document.createTextNode(i)
        const modelNode = document.createTextNode(ItemList[i].Model)
        const typeNode = document.createTextNode(ItemList[i].Type);
        const byNode = document.createTextNode(checkedOutBy);
        const dateNode = document.createTextNode(checkOutDate);

        idElem.appendChild(idNode);
        modelElem.appendChild(modelNode);
        typeElem.appendChild(typeNode);
        checkedOutByElem.appendChild(byNode);
        checkOutDateElem.appendChild(dateNode);

        let html = document.createElement('tr');

        html.appendChild(idElem);
        html.appendChild(modelElem);
        html.appendChild(typeElem);
        html.appendChild(checkedOutByElem);
        html.appendChild(checkOutDateElem);

        tbody.appendChild(html);
    }    
}

itemsDb.on("value", function(snapshot){
    fillTable(snapshot.val());
}, function(err){
    console.log(err);
});