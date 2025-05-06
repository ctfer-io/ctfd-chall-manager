
// convert Local into UTC
document.getElementById('until-input-local').addEventListener('change', function() {
  var datetimeLocal = document.getElementById("until-input-local").value;  
  var datetimeUTC =(new Date(datetimeLocal)).toISOString().split('.')[0] + 'Z'; // remove .000Z of the ISOString format
  document.getElementById("until-input-utc").value = datetimeUTC;
});

// upload scenario as file type=standard
function sendFile(file){
  return new Promise(function(resolve, reject) {
    var formData = new FormData();
    formData.append('file', file);
    formData.append('nonce', CTFd.config.csrfNonce);
    formData.append('type', 'standard') // explicit configuration

    $.ajax({
      url: '/api/v1/files',
      type: 'POST',
      data: formData,
      processData: false,
      contentType: false,
      credentials: 'same-origin', // Include credentials
      success: function(response){
        resolve(response); // Résoudre la promesse avec la réponse de la requête AJAX
      },
      error: function(xhr, status, error){
        reject(error); // Rejeter la promesse avec l'erreur de la requête AJAX
      }
    });
  });
}

// upload scenario as file type=standard
function deleteFile(id){
  return new Promise(function(resolve, reject) {
    var formData = new FormData();
    formData.append('nonce', CTFd.config.csrfNonce);


    $.ajax({
      url: `/api/v1/files/${id}`,
      type: 'DELETE',
      data: formData,
      processData: false,
      contentType: false,
      credentials: 'same-origin', // Include credentials
      success: function(response){
        resolve(response); // Résoudre la promesse avec la réponse de la requête AJAX
      },
      error: function(xhr, status, error){
        reject(error); // Rejeter la promesse avec l'erreur de la requête AJAX
      }
    });
  });
}

CTFd.plugin.run((_CTFd) => {
    const $ = _CTFd.lib.$
    const md = _CTFd.lib.markdown()
});

// auto send the scenario
document.getElementById('scenario').addEventListener('change', function(event) {
  if (event.target.files.length > 0) {
      // send file and get filesId
      if (document.getElementById('scenario_id').value) {
        // delete previous file upload
        deleteFile(document.getElementById('scenario_id').value)
      }

      sendFile(event.target.files[0]).then(function(response) {
        document.getElementById('scenario_id').value = response.data[0].id ;
      });
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
