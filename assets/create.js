
// convert Local into UTC
document.getElementById('until-input-local').addEventListener('change', function() {
  var datetimeLocal = document.getElementById("until-input-local").value;  
  var datetimeUTC =(new Date(datetimeLocal)).toISOString().split('.')[0] + 'Z'; // remove .000Z of the ISOString format
  document.getElementById("until-input-utc").value = datetimeUTC;
});

CTFd.plugin.run((_CTFd) => {
    const $ = _CTFd.lib.$
    const md = _CTFd.lib.markdown()
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
  const jsonData = generateAdditionalJson();

  // Display with a pop-up
  CTFd.ui.ezq.ezAlert({
    title: "Info",
    body: "additional is "+ JSON.stringify(jsonData),
    button: "OK",
  });

  document.getElementById('additional-json').value = JSON.stringify(jsonData)
}
