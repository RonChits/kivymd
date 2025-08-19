// Express API for user signup/login and game history (MongoDB Atlas)
const express = require('express');
const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');
const cors = require('cors');
const app = express();
const PORT = process.env.PORT || 8080;

// Your MongoDB Atlas connection string
const MONGO_URI = 'mongodb+srv://richitsatso:zPd0W0OJFujsgRW0@cluster0.p65ae29.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0';

// Connect to MongoDB
mongoose.connect(MONGO_URI, { 
  useNewUrlParser: true, 
  useUnifiedTopology: true 
})
.then(() => console.log('MongoDB connected successfully'))
.catch(err => {
  console.error('MongoDB connection error:', err);
  process.exit(1); // Exit process if MongoDB connection fails
});

const UserSchema = new mongoose.Schema({
  username: { type: String, unique: true },
  password: String,
});

const HistorySchema = new mongoose.Schema({
  winner: String,
  loser: String,
  playedAt: { type: Date, default: Date.now },
});

const User = mongoose.model('User', UserSchema);
const History = mongoose.model('History', HistorySchema);

// Enhanced CORS configuration
app.use(cors({
  origin: true, // Allow all origins (or specify your domain in production)
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With']
}));

// Handle preflight requests
app.options('*', cors());

// Body parsing middleware
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Health check endpoint
app.get('/health', (req, res) => {
  res.status(200).json({ 
    status: 'OK', 
    message: 'Server is running',
    timestamp: new Date().toISOString(),
    database: mongoose.connection.readyState === 1 ? 'Connected' : 'Disconnected'
  });
});

// Signup endpoint
app.post('/signup', async (req, res) => {
  try {
    const { username, password } = req.body;
    
    if (!username || !password) {
      return res.status(400).json({ error: 'Missing fields' });
    }
    
    const hash = await bcrypt.hash(password, 10);
    const user = new User({ username, password: hash });
    await user.save();
    
    res.json({ success: true });
  } catch (e) {
    if (e.code === 11000) {
      return res.status(409).json({ error: 'Username exists' });
    }
    console.error('Signup error:', e);
    res.status(500).json({ error: 'Server error: ' + e.message });
  }
});

// Login endpoint
app.post('/login', async (req, res) => {
  try {
    const { username, password } = req.body;
    
    if (!username || !password) {
      return res.status(400).json({ error: 'Missing fields' });
    }
    
    const user = await User.findOne({ username });
    if (!user) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }
    
    const valid = await bcrypt.compare(password, user.password);
    if (!valid) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }
    
    res.json({ success: true });
  } catch (e) {
    console.error('Login error:', e);
    res.status(500).json({ error: 'Server error: ' + e.message });
  }
});

// Save game history
app.post('/history', async (req, res) => {
  try {
    const { winner, loser } = req.body;
    
    if (!winner || !loser) {
      return res.status(400).json({ error: 'Missing fields' });
    }
    
    const history = new History({ winner, loser });
    await history.save();
    
    res.json({ success: true });
  } catch (e) {
    console.error('History save error:', e);
    res.status(500).json({ error: 'Server error: ' + e.message });
  }
});

// Get game history for a user
app.get('/history/:username', async (req, res) => {
  try {
    const { username } = req.params;
    const games = await History.find({ 
      $or: [{ winner: username }, { loser: username }] 
    }).sort({ playedAt: -1 }).limit(50);
    
    res.json(games);
  } catch (e) {
    console.error('History fetch error:', e);
    res.status(500).json({ error: 'Server error: ' + e.message });
  }
});

// Root endpoint
app.get('/', (req, res) => {
  res.send('Account server is running!');
});

// Handle 404 errors
app.use('*', (req, res) => {
  res.status(404).json({ error: 'Endpoint not found' });
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error('Unhandled error:', err);
  res.status(500).json({ error: 'Internal server error' });
});

// Start server
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Account server running on port ${PORT}`);
});

// Handle process termination
process.on('SIGINT', () => {
  console.log('Shutting down gracefully');
  mongoose.connection.close();
  process.exit(0);
});

// Handle uncaught exceptions
process.on('uncaughtException', (err) => {
  console.error('Uncaught Exception:', err);
  process.exit(1);
});

process.on('unhandledRejection', (err) => {
  console.error('Unhandled Rejection:', err);
  process.exit(1);
});
