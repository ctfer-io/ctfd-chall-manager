// This script cancel POST call defined in templates/chall_manager_config.html to use CTFd PATCH method


const $ = CTFd.lib.$;

$(".config-section > form:not(.form-upload)").submit(async function (event) {
    event.preventDefault();
    
    const obj = $(this).serializeJSON();
    const params = {};
    for (let x in obj) {
        // convert string to boolean
        if (obj[x] === "true") {
            params[x] = true;
        } else if (obj[x] === "false") {
            params[x] = false;

        // let in string by default
        } else {
            params[x] = obj[x];
        }
    }
    params['chall-manager:refresh'] = btoa(+new Date).slice(-7, -2);

    await CTFd.api.patch_config_list({}, params);
    location.reload();
});
