// Function to fetch the season data from the JSON file
fetch('../season_20242025.json')
    .then(response => response.json())
    .then(data => {
        // Assuming the structure of the data has player stats, with player data having 'name', 'sweater_number', 'points', etc.
        // Map the data to the appropriate stats
        const playersData = data.map(player => {
            return {
                name: player.name,  // Player's name
                sweaterNumber: player.sweater_number,  // Player's sweater number
                points: player.featuredStats?.regularSeason?.subSeason?.points,  // Correct path to points
                goals: player.featuredStats?.regularSeason?.subSeason?.goals,  // Correct path to goals
                assists: player.featuredStats?.regularSeason?.subSeason?.assists,  // Correct path to assists
                photoLink: player.photo_link  // Player's photo link
            };
        });

        // Load the table with the player data
        loadTableData(playersData);
    })
    .catch(error => console.error("Error loading season data:", error));

// Function to dynamically populate the table
function loadTableData(players) {
    const tableBody = document.querySelector("#playersTable tbody");
    tableBody.innerHTML = ''; // Clear any existing rows

    players.forEach(player => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${player.name}</td>
            <td>${player.sweaterNumber}</td>
            <td>${player.points}</td>
            <td>${player.goals}</td>
            <td>${player.assists}</td>
            <td><img src="${player.photoLink}" alt="${player.name}'s photo"></td>
        `;
        tableBody.appendChild(row);
    });
}

// Function to sort the table by column
function sortTable(columnIndex) {
    const rows = Array.from(document.querySelectorAll("#playersTable tbody tr"));
    const isNumeric = columnIndex > 1; // Points, Goals, Assists, and Jersey Number are numeric

    rows.sort((rowA, rowB) => {
        const cellA = rowA.cells[columnIndex].textContent.trim();
        const cellB = rowB.cells[columnIndex].textContent.trim();

        if (isNumeric) {
            return parseFloat(cellA) - parseFloat(cellB);
        } else {
            return cellA.localeCompare(cellB);
        }
    });

    // Reattach sorted rows to the table
    const tableBody = document.querySelector("#playersTable tbody");
    rows.forEach(row => tableBody.appendChild(row));
}
