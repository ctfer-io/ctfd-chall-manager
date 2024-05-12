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


$('#instances-delete-button').click(function (e) {
    let sourceId = $("input[data-source-id]:checked").map(function () {
        return $(this).data("source-id");
    });

    let challengeId = $("input[data-challenge-id]:checked").map(function () {
        return $(this).data("challenge-id");
    });

    let challengeIds = challengeId.toArray()
    let sourceIds = sourceId.toArray()

    CTFd.ui.ezq.ezQuery({
        title: "Delete Containers",
        body: `Are you sure you want to delete the selected ${sourceId.length} instance(s)?`,
        success: async function () {
            for (let i=0; i< sourceId.length; i++){
                console.log(challengeIds[i], sourceIds[i])
                await delete_instance(challengeIds[i], sourceIds[i])
            }
            //await Promise.all(users.toArray().map((user) => delete_container(user)));
            location.reload();
        }
    });
});

$('#instances-renew-button').click(function (e) {
    let sourceId = $("input[data-source-id]:checked").map(function () {
        return $(this).data("source-id");
    });

    let challengeId = $("input[data-challenge-id]:checked").map(function () {
        return $(this).data("challenge-id");
    });

    let challengeIds = challengeId.toArray()
    let sourceIds = sourceId.toArray()

    CTFd.ui.ezq.ezQuery({
        title: "Delete Containers",
        body: `Are you sure you want to delete the selected ${sourceId.length} instance(s)?`,
        success: async function () {
            for (let i=0; i< sourceId.length; i++){
                console.log(challengeIds[i], sourceIds[i])
                await renew_instance(challengeIds[i], sourceIds[i])
            }
            //await Promise.all(users.toArray().map((user) => delete_container(user)));
            location.reload();
        }
    });
});

