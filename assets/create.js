
CTFd.plugin.run((_CTFd) => {
    const $ = _CTFd.lib.$
    const md = _CTFd.lib.markdown()
});

// const helpers = CTFd.helpers;

// Override the challenge update form submission handler
$("#create-chal-entry-div form").submit(function (event) {
  event.preventDefault();
  let curr_challenge_id ;
  
  // Default part defined by CTFd 3.7.0
  const params = $("#create-chal-entry-div form").serializeJSON();
  CTFd.fetch("/api/v1/challenges", {
    method: "POST",
    credentials: "same-origin",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify(params),
  })
    .then(function (response) {
      return response.json();
    })
    .then(function (response) {
      if (response.success) {
        curr_challenge_id = response.data.id // save the id for the plugins
        $("#challenge-create-options #challenge_id").val(
          response.data.id,
        );
        $("#challenge-create-options").modal();
      } else {
        let body = "";
        for (const k in response.errors) {
          body += response.errors[k].join("\n");
          body += "\n";
        }

        ezAlert({
          title: "Error",
          body: body,
          button: "OK",
        });
      } // or find a way to detect changes on $("#challenge-create-options #challenge_id").val()
    }).then(function(){
      const input = document.getElementById('scenario');
      const file = input.files[0]; // Get the first file selected

      if (file) {
        const formData = new FormData();
        formData.append('file', file);
        // send scenario
        CTFd.fetch("/api/v1/files", {
          method: 'POST',
          credentials: 'same-origin',
          body: formData,
        }).then(function (response){
          console.log(response)
      })}})});
      
        // readFileContent(file).then(({ fileName, byteArray }) => {

        // console.log("[PLUGIN] Chall-manager upload scenario to CTFd")
        // let url = "/api/v1/files";

        // var params = {
        //   Name: fileName,
        //   Content: byteArray
        // }

        // CTFd.fetch(url, {
        //   method: 'POST',
        //   credentials: 'same-origin',
        //   headers: {
        //       'Accept': 'application/json',
        //       'Content-Type': 'application/json'
        //   },
        //   body: params
        // }).then(function (response){
        //   console.log(response)
        // })})}})});







        // send file to CTFd


      
    // }).then(function (){ // Plugin chall-manager create scenario
    //     console.log("[PLUGIN] Chall-manager create scenario")
    //     

    //     // var params = {
    //     //   challengeId: curr_challenge_id,
    //     //   scenario_location, scenario_id
    //     // }

    //     CTFd.fetch(url, {
    //         method: 'POST',
    //         credentials: 'same-origin',
    //         headers: {
    //             'Accept': 'application/json',
    //             'Content-Type': 'application/json'
    //         }
    //         //, body: JSON.stringify(params)
    //     }).then(function (response) {
    //         if (response.status === 429) {
    //             // User was ratelimited but process response
    //             return response.json();
    //         }
    //         if (response.status === 403) {
    //             // User is not logged in or CTF is paused.
    //             return response.json();
    //         }
    //         return response.json();
    //     })
    //   });

      
      // Promise.all([
      //   // Upload files
      //   new Promise(function (resolve, _reject) {
      //     console.log("[PLUGIN] Promise")
      //     let form = event.target;
      //     console.log(form)
      //     let filepath = $(form.elements["scenario"]).val();
      //     console.log(filepath)
      //     if (filepath) {
      //       console.log("[PLUGIN] Upload scenario")
      //       // CTFd.helpers.files.upload(form);
      //       CTFd.plugin.run(CTFd.helpers.files.upload(form))
      //     }
      //     resolve();
      //   })
      // ]);
    


function readFileContent(file) {
  return new Promise((resolve, reject) => {
      if (file) {
          var reader = new FileReader();

          // Définir la fonction de rappel à exécuter lorsque la lecture est terminée
          reader.onload = function(event) {
              // Convertir le contenu en Uint8Array
              var buffer = event.target.result;
              var byteArray = new Uint8Array(buffer);
              var fileName = file.name;
              resolve({ fileName, byteArray });
          };

          // Gestion d'erreur de lecture
          reader.onerror = function(event) {
              reject(event.target.error);
          };

          // Lire le contenu du fichier en tant qu'array buffer
          reader.readAsArrayBuffer(file);
      } else {
          reject("Aucun fichier sélectionné.");
      }
  });
}