function isNumberInRange(object) {
    var value = parseFloat(object.value);
    var step = parseFloat(object.step);

    value = value - floatSafeRemainder(value, step);

    object.value = value;

    if (value > parseFloat(object.max))
        object.value = object.max;
    else if (value < parseFloat(object.min))
        object.value = object.min;
}

function floatSafeRemainder(val, step) {
    var valDecCount = (val.toString().split('.')[1] || '').length;
    var stepDecCount = (step.toString().split('.')[1] || '').length;
    var decCount = valDecCount > stepDecCount ? valDecCount : stepDecCount;
    var valInt = parseInt(val.toFixed(decCount).replace('.', ''));
    var stepInt = parseInt(step.toFixed(decCount).replace('.', ''));
    return (valInt % stepInt) / Math.pow(10, decCount);
}

function isNumeric(evt) {
    var theEvent = evt || window.event;
    var key = theEvent.keyCode || theEvent.which;
    key = String.fromCharCode(key);
    var regex = /[0-9]|\./;
    if (!regex.test(key)) {
        theEvent.returnValue = false;
        if (theEvent.preventDefault) theEvent.preventDefault();
    }
}