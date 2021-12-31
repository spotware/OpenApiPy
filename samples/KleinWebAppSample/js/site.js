$(document).ready(function () {
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    const token = urlParams.get("token");

    $("#sendButton").click(function () {
        $.getJSON(`/get-data?token=${token}&command=${$('#commandInput').val()}`, function (data, status, xhr) {
            response = "result" in data ? data["result"] : JSON.stringify(data)
            if ($("#outputTextarea").val() == "") {
                $("#outputTextarea").val(response + "\n").change()
            }
            else {
                $("#outputTextarea").val($("#outputTextarea").val() + "\n" + response + "\n").change()
            }
        });
    });
});
