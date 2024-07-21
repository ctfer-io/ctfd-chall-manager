// selector for janitoring method
document.getElementById('select-option').addEventListener('change', function() {
  displayJanitorStrategy()  
});

function displayJanitorStrategy(){
  var selectedOption = document.getElementById('select-option').value
  if (selectedOption === 'until') {
    document.getElementById('cm-mode-until').style.display = 'block';
    document.getElementById('cm-mode-timeout').style.display = 'none';
    document.getElementById('timeout-input').required = false;
    document.getElementById('until-input-local').required = true;
    document.getElementById('timeout-input').value = ''; // Reset timeout input
  } else if (selectedOption === 'timeout') {
    document.getElementById('cm-mode-until').style.display = 'none';
    document.getElementById('cm-mode-timeout').style.display = 'block';
    document.getElementById('until-input-local').required = false;
    document.getElementById('timeout-input').required = true;
    document.getElementById('until-input-local').value = ''; // Reset until input
    document.getElementById('until-input-utc').value = ''; // Reset until input
  } else {
    document.getElementById('cm-mode-until').style.display = 'none';
    document.getElementById('cm-mode-timeout').style.display = 'none';
    document.getElementById('timeout-input').required = false;
    document.getElementById('until-input-local').required = false; 
    document.getElementById('until-input-local').value = ''; // Reset until input
    document.getElementById('until-input-utc').value = ''; // Reset until input
    document.getElementById('timeout-input').value = ''; // Reset timeout input    
  }
}


// convert Local into UTC
document.getElementById('until-input-local').addEventListener('change', function() {
  var datetimeLocal = document.getElementById("until-input-local").value;  
  var datetimeUTC =(new Date(datetimeLocal)).toISOString();
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
