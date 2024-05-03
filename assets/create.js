// import { default as helpers } from "../../../themes/admin/assets/js/compat/helpers";

CTFd.plugin.run((_CTFd) => {
    const $ = _CTFd.lib.$
    const md = _CTFd.lib.markdown()
    // const helpers = _CTFd.helpers
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
    }).then(function (){ // Plugin chall-manager create scenario
        console.log("[PLUGIN] Chall-manager create scenario")
        let url = "/api/v1/plugins/ctfd-chall-manager/admin/scenario?challenge_id=" + curr_challenge_id + "&scenario=pouet";
        // let data = {
        //   challenge_id: curr_challenge_id,
        //   scenario, scenario_id,
        // }
        CTFd.fetch(url, {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        }).then(function (response) {
            if (response.status === 429) {
                // User was ratelimited but process response
                return response.json();
            }
            if (response.status === 403) {
                // User is not logged in or CTF is paused.
                return response.json();
            }
            return response.json();
        })
      });


      Promise.all([
        // Upload files
        new Promise(function (resolve, _reject) {
          console.log("[PLUGIN] Promise")
          let form = event.target;
          console.log(form)
          let filepath = $(form.elements["scenario"]).val();
          console.log(filepath)
          if (filepath) {
            console.log("[PLUGIN] Upload scenario")
            // CTFd.helpers.files.upload(form);
            CTFd.plugin.run(CTFd.helpers.files.upload(form))
          }
          resolve();
        })
      ]);
    
});

// const files = {
//   upload: (form, extra_data, cb) => {
//     const CTFd = window.CTFd;
//     if (form instanceof jQuery) {
//       form = form[0];
//     }
//     var formData = new FormData(form);
//     formData.append("nonce", CTFd.config.csrfNonce);
//     for (let [key, value] of Object.entries(extra_data)) {
//       formData.append(key, value);
//     }

//     var pg = ezq.ezProgressBar({
//       width: 0,
//       title: "Upload Progress",
//     });
//     $.ajax({
//       url: CTFd.config.urlRoot + "/api/v1/files",
//       data: formData,
//       type: "POST",
//       cache: false,
//       contentType: false,
//       processData: false,
//       xhr: function () {
//         var xhr = $.ajaxSettings.xhr();
//         xhr.upload.onprogress = function (e) {
//           if (e.lengthComputable) {
//             var width = (e.loaded / e.total) * 100;
//             pg = ezq.ezProgressBar({
//               target: pg,
//               width: width,
//             });
//           }
//         };
//         return xhr;
//       },
//       success: function (data) {
//         form.reset();
//         pg = ezq.ezProgressBar({
//           target: pg,
//           width: 100,
//         });
//         setTimeout(function () {
//           pg.modal("hide");
//         }, 500);

//         if (cb) {
//           cb(data);
//         }
//       },
//     });
//   },
// };