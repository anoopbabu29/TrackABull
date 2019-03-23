let list =[
    {
        model: "S10",
        type: "phone",
        isCheckedOut: true,
        checkOutDate: "3/22/19 3:00 PM",
        checkedOutBy: "Jose"
    },
    {
        model: "iphun",
        type: "phone",
        isCheckedOut: true,
        checkOutDate: "3/21/19 3:00 PM",
        checkedOutBy: "anup"
    }
]

function fillTable(ItemList) {
    let tbody = document.getElementById('itemTableBody');
    tbody.innerHTML = "";

    for(let i = 0; i < ItemList.length; i++){
        let id = document.createElement(i+1);
        let model = document.createElement('td');
        let type = document.createElement('td');
        let isCheckedOut = document.createElement('td');
        let checkOutDate = document.createElement('td');
        let checkedOutBy = document.createElement('td');

        const idNode = document.createTextNode(id)
        const modelNode = document.createTextNode(ItemList[i].model)
        const typeNode = document.createTextNode(ItemList[i].type);
        const isCheckedNode = document.createTextNode(ItemList[i].isCheckedOut);
        const dateNode = document.createTextNode(ItemList[i].checkedOutBy);
        const byNode = document.createTextNode(ItemList[i].checkOutDate);

        id.appendChild(idNode);
        model.appendChild(modelNode);
        type.appendChild(typeNode);
        isCheckedOut.appendChild(isCheckedNode);
        checkedOutBy.appendChild(dateNode);
        checkOutDate.appendChild(byNode);

        let html = document.createElement('tr');

        html.appendChild(id);
        html.appendChild(model);
        html.appendChild(type);
        html.appendChild(isCheckedOut);
        html.appendChild(checkedOutBy);
        html.appendChild(checkOutDate);

        tbody.appendChild(html);
    }    
}