
// convert Local into UTC
document.getElementById('until-input-local').addEventListener('change', function() {
  console.log("pouet")
  var datetimeLocal = document.getElementById("until-input-local").value;  
  if (datetimeLocal != "") {
    var datetimeUTC =(new Date(datetimeLocal)).toISOString();
    document.getElementById("until-input-utc").value = datetimeUTC;
  } else {
    document.getElementById("until-input-utc").value = ""
  }
});

function addRow() {
  const table = document.getElementById('additional-configuration').getElementsByTagName('tbody')[0];
  const newRow = table.insertRow();
  
  const actionCell = newRow.insertCell(0);
  const keyCell = newRow.insertCell(1);
  const valueCell = newRow.insertCell(2);

  keyCell.innerHTML = '<input type="text" class="form-control" placeholder="Key">';
  valueCell.innerHTML = '<input type="text" class="form-control" placeholder="Value">';
  actionCell.innerHTML = '<button class="btn btn-link p-0 text-danger" data-placement="top" data-toggle="tooltip" onclick="deleteRow(this)"><i class="fa-solid fa-xmark"></i></button>';
}                     

// Function to delete a row
function deleteRow(button) {
  const row = button.closest('tr');
  row.remove();
}


function displayCurrentUntil() {
  var datetimeUTC = document.getElementById("until-input-utc").value; 
  if (datetimeUTC) {
    var datetimeLocal = new Date(datetimeUTC);

    // Format the local date to match 'datetime-local' input format
    var formattedLocalDate = datetimeLocal.toISOString().slice(0, 16); // Format: YYYY-MM-DDTHH:mm

    // Set the formatted local date to the datetime-local input
    document.getElementById("until-input-local").value = formattedLocalDate;
  }
}

function displayCurrentAdditional() {
  const jsonData = JSON.parse(document.getElementById('current-additional-json').value);
  console.log(jsonData)
  const table = document.getElementById('additional-configuration').getElementsByTagName('tbody')[0];
  // const rows = table.getElementsByTagName('tr');

  Object.keys(jsonData).forEach(function(key) {
    const newRow = table.insertRow();
    const actionCell = newRow.insertCell(0);
    const keyCell = newRow.insertCell(1);
    const valueCell = newRow.insertCell(2);
    keyCell.innerHTML = '<input type="text" class="form-control" placeholder="Key" value="' + key + '">';
    valueCell.innerHTML = '<input type="text" class="form-control" placeholder="Value" value="' + jsonData[key] + '">';
    actionCell.innerHTML = '<button class="btn btn-link p-0 text-danger" data-placement="top" data-toggle="tooltip" onclick="deleteRow(this)"><i class="fa-solid fa-xmark"></i></button>';
  });
}

// parse the additional configuration add  generate the associated json
function generateAdditionalJson(){
  const table = document.getElementById('additional-configuration').getElementsByTagName('tbody')[0];
  const rows = table.getElementsByTagName('tr');
  const jsonData = {};
  for (let i = 0; i < rows.length; i++) {
    const key = rows[i].cells[1].getElementsByTagName('input')[0].value;
    const value = rows[i].cells[2].getElementsByTagName('input')[0].value;
    jsonData[key] = value;
  }
  return jsonData;
}

function applyAdditional() {
  const jsonDataOld = JSON.parse(document.getElementById('current-additional-json').value);
  const jsonDataNew = generateAdditionalJson();
  // Display with a pop-up
  CTFd.ui.ezq.ezAlert({
    title: "Info",
    body: "Old additional is : " + JSON.stringify(jsonDataOld) + "<br>New addtional is : "+ JSON.stringify(jsonDataNew),
    button: "OK",
  });

  document.getElementById('additional-json').value = JSON.stringify(jsonDataNew)
}


displayCurrentUntil()
displayCurrentScenario()
displayCurrentAdditional()

