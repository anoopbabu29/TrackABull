var config = {
    apiKey: "AIzaSyA4s65NGcz_9EfKiPmfFKmN9brXwYR7BcU",
    authDomain: "track-a-bull.firebaseapp.com",
    databaseURL: "https://track-a-bull.firebaseio.com",
    projectId: "track-a-bull",
    storageBucket: "track-a-bull.appspot.com",
    messagingSenderId: "819088197621"
};
firebase.initializeApp(config);

let interactionsDb = firebase.database().ref('/Interactions/');
let fireFunct = firebase.functions();

let filtList;

function fillTable(ItemList) {
    let tbody = document.getElementById('itemTableBody');
    tbody.innerHTML = "";

    ItemList.shift();

    const byName = R.groupBy(function(student) {
        if(student.Returned == null){
            return student.Name;
        }
    });
    
    filtList = byName(ItemList);

    console.log(filtList)

    let i = 0;
    for (const person in filtList) {
        if (person == 'undefined' || person == 'null'){
            continue;
        }
        i++;
        const idElem = document.createElement('td');
        const nameElem = document.createElement('td');
        const numItemsElem = document.createElement('td');
        const buttonTdElem = document.createElement('td');

        const idNode = document.createTextNode(i)
        const nameNode = document.createTextNode(person)
        const numItemsNode = document.createTextNode(filtList[person].length);
        
        buttonTdElem.innerHTML = '<a class="btn btn-outline-info modalItems" role="button" data-toggle="modal" data-target="#ModalCenter">View Items</a>'

        idElem.appendChild(idNode);
        nameElem.appendChild(nameNode);
        numItemsElem.appendChild(numItemsNode);

        let html = document.createElement('tr');

        html.id = 'user' + i;

        html.appendChild(idElem);
        html.appendChild(nameElem);
        html.appendChild(numItemsElem);
        html.appendChild(buttonTdElem);

        tbody.appendChild(html);
    }

    addEventListeners();
}

interactionsDb.on("value", function(snapshot){
    fillTable(snapshot.val());
}, function(err){
    console.log(err);
});


function addEventListeners() {
    var btnList = document.body.getElementsByClassName('modalItems');

    for (const btn of btnList) {
        const tr = btn.parentNode.parentNode;
        btn.addEventListener('click', function(){loadModal(tr.id)} );
    }
}

function loadModal(id){
    const userId = document.getElementById(id);
    const modalTitle = document.getElementById('ModalTitle')
    const name = userId.children[1].innerText
    modalTitle.innerText = "Items checked out by " + name

    fillModalTable(filtList[name])
}

function fillModalTable(ItemList) {
    let tbody = document.getElementById('modalTableBody');
    tbody.innerHTML = "";

    for(let i = 0; i < ItemList.length; i++){
        const idElem = document.createElement('td');
        const modelElem = document.createElement('td');
        const checkOutDateElem = document.createElement('td');

        const idNode = document.createTextNode(i+1)
        const modelNode = document.createTextNode(ItemList[i].Item)
        const dateNode = document.createTextNode(ItemList[i].CheckOut);

        idElem.appendChild(idNode);
        modelElem.appendChild(modelNode);
        checkOutDateElem.appendChild(dateNode);

        let html = document.createElement('tr');

        html.appendChild(idElem);
        html.appendChild(modelElem);
        html.appendChild(checkOutDateElem);

        tbody.appendChild(html);
    }    
}