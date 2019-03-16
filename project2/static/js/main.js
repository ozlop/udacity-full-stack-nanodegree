var formFields = ['year', 'make', 'model', 'sub_model', 'engine_displacement',
                  'engine_code', 'fuel_type', 'market', 'submit']

function disableFields(formFields) {
    for (let field of formFields) {
        if (field != 'year') {
        document.getElementById(field).disabled = true;
        }
        if (field != 'submit') {
        document.getElementById(field).value ='';
        }
    }
}
window.onload = function() {
    disableFields(formFields)
};
let year_select = document.getElementById('year');
let make_select = document.getElementById('make');
let model_select = document.getElementById('model');
let sub_model_select = document.getElementById('sub_model');
let engine_displacement_select = document.getElementById('engine_displacement');
let engine_code_select = document.getElementById('engine_code');
let fuel_type_select = document.getElementById('fuel_type');
let market_select = document.getElementById('market');

year_select.onchange = function() {
    yearFormFields = formFields.filter(function(e) { return e !== 'year' })
    yearValue = year_select.value;
    disableFields(yearFormFields)
    if (yearValue === ' ') { disableFields(yearFormFields) }
    else { document.getElementById('make').disabled = false }
    yearFormFields = yearFormFields.filter(function(e) { return e !== 'make' })

    fetch('/select/make/' + yearValue).then(function(response) {
        response.json().then(function(data) {
            let makeOptionHTML = '';
            makeOptionHTML = '<option value=" "> </option>';

            for (let make of data.makes) {
                makeOptionHTML += '<option value="' + make.make + '">' + make.make + '</option>';
            }

            make_select.innerHTML = makeOptionHTML;
        });
    });
}
make_select.onchange = function() {
    makeValue = make_select.value;
    disableFields(yearFormFields)
    if (makeValue === ' ') { disableFields(yearFormFields) }
    else { document.getElementById('model').disabled = false }
    makeFormFields = yearFormFields.filter(function(e) { return e !== 'model' })

    fetch('/select/model/' + yearValue + '/' + makeValue).then(function(response) {
        response.json().then(function(data) {
            let modelOptionHTML = '';
            modelOptionHTML = '<option value=" "> </option>';

            for (let model of data.models) {
                modelOptionHTML += '<option value="' + model.model + '">' + model.model + '</option>';
            }

            model_select.innerHTML = modelOptionHTML;
        });
    });
}
model_select.onchange = function() {
    modelValue = model_select.value;
    disableFields(makeFormFields)
    if (modelValue === ' ') { disableFields(makeFormFields) }
    else { document.getElementById('sub_model').disabled = false }
    modelFormFields = makeFormFields.filter(function(e) { return e !== 'sub_model' })

    fetch('/select/sub_model/' + yearValue + '/' + makeValue + '/' + modelValue).then(function(response) {
        response.json().then(function(data) {
            let subModelOptionHTML = '';
            subModelOptionHTML = '<option value=" "> </option>';

            for (let sub_model of data.sub_models) {
                if (sub_model.sub_model == 'N/A') {
                    subModelOptionHTML += '<option value="None">N/A</option>';
                } else {
                    subModelOptionHTML += '<option value="' + sub_model.sub_model + '">' + sub_model.sub_model + '</option>';
                }
            }

            sub_model_select.innerHTML = subModelOptionHTML;
        });
    });
}
sub_model_select.onchange = function() {
    if (sub_model_select.value != 'N/A') {
        subModelValue = sub_model_select.value;
    }
    else {
        subModelValue = 'None'
    }
    disableFields(modelFormFields)
    if (subModelValue === ' ') { disableFields(modelFormFields) }
    else { document.getElementById('engine_displacement').disabled = false }
    subModelFormFields = modelFormFields.filter(function(e) { return e !== 'engine_displacement' })

    fetch('/select/engine_displacement/' + yearValue + '/' + makeValue + '/' + modelValue + '/' + subModelValue).then(function(response) {
        response.json().then(function(data) {
            let engineDisplacementOptionHTML = '';
            engineDisplacementOptionHTML += '<option value=" "> </option>';

            for (let engine_displacement of data.engine_displacements) {
                engineDisplacementOptionHTML += '<option value="' + engine_displacement.engine_displacement + '">' + engine_displacement.engine_displacement + '</option>';
            }

            engine_displacement_select.innerHTML = engineDisplacementOptionHTML;
        });
    });
}
engine_displacement_select.onchange = function() {
    engineDisplacementValue = engine_displacement_select.value;
    disableFields(subModelFormFields)
    if (engineDisplacementValue === ' ') { disableFields(subModelFormFields) }
    else { document.getElementById('engine_code').disabled = false }
    engineDisplacementFormFields = subModelFormFields.filter(function(e) { return e !== 'engine_code' })

    fetch('/select/engine_code/' + yearValue + '/' + makeValue + '/' + modelValue + '/' + subModelValue + '/' + engineDisplacementValue).then(function(response) {
        response.json().then(function(data) {
            let engineCodeOptionHTML = '';
            engineCodeOptionHTML += '<option value=" "> </option>';

            for (let engine_code of data.engine_codes) {
                if (engine_code.engine_code == 'N/A') {
                    engineCodeOptionHTML += '<option value="None">N/A</option>';
                } else {
                    engineCodeOptionHTML += '<option value="' + engine_code.engine_code + '">' + engine_code.engine_code + '</option>';
                }
            }

            engine_code_select.innerHTML = engineCodeOptionHTML;
        });
    });
}
engine_code_select.onchange = function() {
    if (engine_code_select.value != 'N/A') {
        engineCodeValue = engine_code_select.value;
    }
    else {
        engineCodeValue = 'None'
    }
    disableFields(engineDisplacementFormFields)
    if (engineCodeValue === ' ') { disableFields(engineDisplacementFormFields) }
    else { document.getElementById('fuel_type').disabled = false }
    engineCodeFormFields = engineDisplacementFormFields .filter(function(e) { return e !== 'fuel_type' })


    fetch('/select/fuel_type/' + yearValue + '/' + makeValue + '/' + modelValue + '/' + subModelValue + '/' + engineDisplacementValue + '/' + engineCodeValue).then(function(response) {
        response.json().then(function(data) {
            let fuelTypeOptionHTML = '';
            fuelTypeOptionHTML += '<option value=" "> </option>';

            for (let fuel_type of data.fuel_types) {
                if (fuel_type.fuel_type == 'N/A') {
                    fuelTypeOptionHTML += '<option value="None">N/A</option>';
                } else {
                    fuelTypeOptionHTML += '<option value="' + fuel_type.fuel_type + '">' + fuel_type.fuel_type + '</option>';
                }
            }

            fuel_type_select.innerHTML = fuelTypeOptionHTML;
        });
    });
}
fuel_type_select.onchange = function() {
    if (fuel_type_select.value != 'N/A') {
        fuelTypeValue = fuel_type_select.value;
    }
    else {
        fuelTypeValue = 'None'
    }
    disableFields(engineCodeFormFields)
    if (fuelTypeValue === ' ') { disableFields(engineCodeFormFields) }
    else { document.getElementById('market').disabled = false }
    fuelTypeFormFields = engineCodeFormFields .filter(function(e) { return e !== 'market' })


    fetch('/select/market/' + yearValue + '/' + makeValue + '/' + modelValue  + '/' + subModelValue + '/' + engineDisplacementValue + '/' + engineCodeValue + '/' + fuelTypeValue).then(function(response) {
        response.json().then(function(data) {
            let marketTypeOptionHTML = '';
            marketTypeOptionHTML += '<option value=" "> </option>';
            for (let market of data.markets) {
                if (market.market == 'N/A') {
                    marketTypeOptionHTML += '<option value="None">N/A</option>';
                } else {
                    marketTypeOptionHTML += '<option value="' + market.market + '">' + market.market + '</option>';
                }
            }

            market_select.innerHTML = marketTypeOptionHTML;
        });
    });
}
market_select.onchange = function() {
    if (market_select.value != 'N/A') {
        marketValue = market_select.value
    }
    else {
        marketValue = 'None'
    }
    if (marketValue === ' ') { disableFields(fuelTypeFormFields) }
    else { document.getElementById('submit').disabled = false }
}
