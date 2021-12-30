$(document).ready(function () {
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    const token = urlParams.get("token");

    $("#sendButton").click(function () {
        $.getJSON(`/get-data?token=${token}&command=${$('#commandInput').val()}`, function (data, status, xhr) {
            if ($("#outputTextarea").val() == "") {
                $("#outputTextarea").val(data["result"]).change()
            }
            else {
                $("#outputTextarea").val($("#outputTextarea").val() + "\n" + data["result"]).change()
            }
        });
    });
});
