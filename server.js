// const express = require("express");
// const bodyParser = require("body-parser");
// const session = require("express-session");
// const multer = require("multer");
// const conn = require("./connection.js");

// const app = express();

// app.use(bodyParser.json());
// app.use(bodyParser.urlencoded({ extended: true }));
// app.use(express.static("public"));

// app.use('/uploads', express.static('uploads'));

// // Set EJS as the view engine
// app.set("view engine", "ejs");
// app.set("views", "./views");

// // Session management
// app.use(
//     session({
//         secret: "your-secret-key",
//         resave: false,
//         saveUninitialized: false,
//         cookie: { maxAge: 6000000 },
//     })
// );


// // Routes
// app.get("/", (req, res) => {
//     res.render("corp_login"); // Render login page
// });

// // Define the login endpoint
// app.post('/login', (req, res) => {
//     const { corporate_id, password } = req.body;

//     // Basic validation (make sure both fields are provided)
//     if (!corporate_id || !password) {
//         return res.status(400).json({ message: 'Corporate ID and password are required' });
//     }

//     // Query the database to find matching corporate_id and password
//     const query = 'SELECT * FROM corporate WHERE id = ? AND password = ?';
//     conn.query(query, [corporate_id, password], (err, results) => {
//         if (err) {
//             console.error('Database query error:', err);
//             return res.status(500).json({ message: 'Internal Server Error' });
//         }

//         if (results.length > 0) {
//             // If credentials match, redirect to /divisions
//             return res.redirect("/divisions");
//         } else {
//             // If credentials don't match, return an error
//             return res.status(401).json({ message: 'Invalid credentials' });
//         }
//     });
// });

// app.get("/divisions", (req, res) => {
//     res.render("divisions");
// });


// // Start the server
// const PORT = 3000;
// app.listen(PORT, () => {
//     console.log(`Server is running on http://localhost:${PORT}`);
// });

const express = require("express");
const bodyParser = require("body-parser");
const session = require("express-session");
const conn = require("./connection.js"); // MySQL connection

const app = express();

// Middleware setup
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));
app.use(express.static("public"));
app.use('/uploads', express.static('uploads'));

// Set EJS as the view engine
app.set("view engine", "ejs");
app.set("views", "./views");

// Session management
app.use(
    session({
        secret: "your-secret-key",
        resave: false,
        saveUninitialized: false,
        cookie: { maxAge: 6000000 },
    })
);

// Routes

// Initial login page
app.get("/", (req, res) => {
    res.render("corp_login"); // Render login page
});

// Handle the login
app.get('/login', (req, res) => {
    const { district, corporate_id, password } = req.query;

    // Basic validation (make sure both fields are provided)
    if (!corporate_id || !password) {
        return res.status(400).json({ message: 'Corporate ID and password are required' });
    }

    // Query the database to find matching corporate_id and password
    const query = 'SELECT * FROM corporate WHERE district = ? AND id = ? AND password = ? ';
    conn.query(query, [district, corporate_id, password], (err, results) => {
        if (err) {
            console.error('Database query error:', err);
            return res.status(500).json({ message: 'Internal Server Error' });
        }

        if (results.length > 0) {
            // If credentials match, store the corporate_id in session
            req.session.corporate_id = results[0].id;
            req.session.district = results[0].district; // Save district from the login
            console.log(req.session.district);
            // Redirect to the divisions page
            return res.redirect("/divisions");
        } else {
            // If credentials don't match, return an error
            return res.status(401).json({ message: 'Invalid credentials' });
        }
    });
});

// app.get("/divisions", (req, res) => {
//     res.render("divisions");
// })

// Display divisions based on the logged-in user's district
app.get("/divisions", (req, res) => {
    if (!req.session.corporate_id) {
        return res.redirect("/"); // If not logged in, redirect to login page
    }

    const district = req.session.district; // Get district from session
    console.log("District from session:", district); // Log the district

    //Query to get the divisions for the logged-in user's district
    const query = `
        SELECT dd.division_id, dd.division_name
        FROM division_details dd
        JOIN corporate c ON c.id = dd.id 
        WHERE c.district = ?`;




    conn.query(query, [district], (err, divisions) => {
        if (err) {
            console.error('Error fetching divisions:', err);
            return res.status(500).send('Error fetching divisions');
        }

        console.log("Fetched divisions:", divisions); // Log the divisions data

        if (divisions.length === 0) {
            return res.status(404).send("No divisions found for this district.");
        }

        // Render divisions page with data from the database
        res.render("divisions", { divisions, district });
    });
});

// Route for displaying divisions and selecting a division
app.post("/division", (req, res) => {
    const { division } = req.body;
    const div_id = parseInt(division, 10);
    console.log(div_id);

    if (!div_id) {
        return res.status(400).json({ message: "Please select a division" });
    }

    // Store division_id in the session
    req.session.division_id = div_id;

    // Redirect to bins_info page
    return res.redirect("/bins_info");
});

app.get("/bins_info", (req, res) => {
    console.log(req.session.division_id)
    const division_id = req.session.division_id;
    console.log(division_id);
    if (!division_id) {
        return res.status(400).json({ message: "No division selected" });
    }

    // Query to fetch bin status for the selected division
    const query = `
        SELECT bin_id, bin_status 
        FROM division_bins
        WHERE division_id = ?`;

    conn.query(query, [division_id], (err, bins) => {
        if (err) {
            console.error('Error fetching bins:', err);
            return res.status(500).send('Error fetching bins');
        }

        if (bins.length === 0) {
            return res.status(404).send("No bins found for this division.");
        }

        // Render bins_info page with bin data
        res.render("bins_info", { bins });
    });
});



// Start the server
const PORT = 3001;
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});