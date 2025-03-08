const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const app = express();
const port = 1000;

// Middleware to serve static files
app.use(express.static(__dirname));

// Connect to your existing SQLite database file
const db = new sqlite3.Database('./db.sqlite3', (err) => {
    if (err) {
        console.error('Error connecting to db.sqlite3:', err.message);
    } else {
        console.log('Connected to db.sqlite3');
    }
});

// Serve the HTML file
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// Endpoint to get unique crops
app.get('/crops', (req, res) => {
    db.all('SELECT DISTINCT product_name FROM store_product', [], (err, rows) => {
        if (err) {
            console.error('Error fetching crops:', err.message);
            return res.status(500).json({ error: 'Error fetching crops' });
        }
        res.json({ crops: rows.map(row => row.product_name) });
    });
});

// Endpoint to get dashboard data
app.get('/dashboard', (req, res) => {
    const crop = req.query.crop;
    if (!crop) {
        return res.status(400).json({ error: 'Crop name is required' });
    }

    const query = `
        SELECT up.state, MIN(sp.price) AS min_price, MAX(sp.price) AS max_price
        FROM store_product sp
        JOIN app_userprofile up ON sp.farmerID = up.id
        WHERE sp.product_name = ?
        GROUP BY up.state
        ORDER BY up.state
    `;
    db.all(query, [crop], (err, rows) => {
        if (err) {
            console.error('Error fetching dashboard data:', err.message);
            return res.status(500).json({ error: 'Error fetching dashboard data' });
        }
        res.json(rows);
    });
});

// Start the server
app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});

// Close the database connection gracefully on server shutdown
process.on('SIGINT', () => {
    db.close((err) => {
        if (err) {
            console.error('Error closing database:', err.message);
        }
        console.log('Database connection closed');
        process.exit(0);
    });
});