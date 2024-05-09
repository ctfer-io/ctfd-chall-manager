async function delete_instance(challengeId, sourceId) {
    let response = await CTFd.fetch("/api/v1/plugins/ctfd-chall-manager/admin/instance?challengeId=" + challengeId + "&sourceId=" + sourceId, {
        method: "DELETE",
        credentials: "same-origin",
        headers: {
            Accept: "application/json",
            "Content-Type": "application/json"
        }
    });
    console.log(response)
    response = await response.json();
    return response;
}

async function renew_instance(challengeId, sourceId) {
    let response = await CTFd.fetch("/api/v1/plugins/ctfd-chall-manager/admin/instance?challengeId=" + challengeId + "&sourceId=" + sourceId, {
        method: "PATCH",
        credentials: "same-origin",
        headers: {
            Accept: "application/json",
            "Content-Type": "application/json"
        }
    });
    console.log(response)
    response = await response.json();
    return response;
}


$(".delete-instance").click(function (e) {
    e.preventDefault();
    let challengeId = $(this).attr("challenge-id");
    let sourceId = $(this).attr("source-id");

    console.log(sourceId)
    console.log(challengeId)

    CTFd.ui.ezq.ezQuery({
        title: "Destroy",
        body: "<span>Are you sure you want to delete this instance?</span>",
        success: async function () {
            await delete_instance(challengeId, sourceId);
            location.reload();
        }
    });
});


$(".renew-instance").click(function (e) {
    e.preventDefault();
    let challengeId = $(this).attr("challenge-id");
    let sourceId = $(this).attr("source-id");

    console.log(sourceId)
    console.log(challengeId)

    CTFd.ui.ezq.ezQuery({
        title: "Renew",
        body: "<span>Are you sure you want to renew this instance?</span>",
        success: async function () {
            await renew_instance(challengeId, sourceId);
            location.reload();
        }
    });
});
