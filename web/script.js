$(document).ready(function () {
    const API_URL = 'http://localhost:4000/api/petitions';

    console.log('Hello from script.js');

    function displayPetitions(petitions, container) {
        petitions.forEach(petition => {
            const petitionDiv = $('<div class="petition"></div>');
            petitionDiv.append(`<h3>${petition.title}</h3>`);
            petitionDiv.append(`<p>${petition.content}</p>`);
            petitionDiv.append(`<p>Option 1: ${petition.option_1} (${petition.votes_option_1} votes)</p>`);
            petitionDiv.append(`<p>Option 2: ${petition.option_2} (${petition.votes_option_2} votes)</p>`);
            $(container).append(petitionDiv);
        });
    }

    $.getJSON(API_URL, function (response) {
        if (response.petitions && Array.isArray(response.petitions)) {
            const openedPetitions = response.petitions.filter(petition => !petition.is_closed);
            const closedPetitions = response.petitions.filter(petition => petition.is_closed);

            displayPetitions(openedPetitions, '#opened-petitions');
            displayPetitions(closedPetitions, '#closed-petitions');
        } else {
            console.error('Unexpected API response format:', response);
        }
    }).fail(function (jqxhr, textStatus, error) {
        console.error('Error fetching data from API:', textStatus, error);
    });
});
