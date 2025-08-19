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
mongoose.connect(MONGO_URI, { useNewUrlParser: true, useUnifiedTopology: true })
  .then(() => console.log('MongoDB connected successfully'))
  .catch(err => console.error('MongoDB connection error:', err));

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

// Middleware
app.use(cors({
  origin: '*',
  methods: ['GET', 'POST'],
  credentials: true
}));
app.use(express.json());

// Signup endpoint
app.post('/signup', async (req, res) => {
  const { username, password } = req.body;
  if (!username || !password) return res.status(400).json({ error: 'Missing fields' });
  try {
    const hash = await bcrypt.hash(password, 10);
    const user = new User({ username, password: hash });
    await user.save();
    res.json({ success: true });
  } catch (e) {
    if (e.code === 11000) return res.status(409).json({ error: 'Username exists' });
    res.status(500).json({ error: 'Server error: ' + e.message });
  }
});

// Login endpoint
app.post('/login', async (req, res) => {
  const { username, password } = req.body;
  try {
    const user = await User.findOne({ username });
    if (!user) return res.status(401).json({ error: 'Invalid credentials' });
    const valid = await bcrypt.compare(password, user.password);
    if (!valid) return res.status(401).json({ error: 'Invalid credentials' });
    res.json({ success: true });
  } catch (e) {
    res.status(500).json({ error: 'Server error: ' + e.message });
  }
});

// Save game history
app.post('/history', async (req, res) => {
  const { winner, loser } = req.body;
  if (!winner || !loser) return res.status(400).json({ error: 'Missing fields' });
  try {
    const history = new History({ winner, loser });
    await history.save();
    res.json({ success: true });
  } catch (e) {
    res.status(500).json({ error: 'Server error: ' + e.message });
  }
});

// Get game history for a user
app.get('/history/:username', async (req, res) => {
  const { username } = req.params;
  try {
    const games = await History.find({ $or: [{ winner: username }, { loser: username }] }).sort({ playedAt: -1 }).limit(50);
    res.json(games);
  } catch (e) {
    res.status(500).json({ error: 'Server error: ' + e.message });
  }
});

// Health check
app.get('/', (req, res) => res.send('Account server is running!'));

// Start server
app.listen(PORT, () => console.log(`Account server running on port ${PORT}`));

// Handle unhandled promise rejections
process.on('unhandledRejection', (err) => {
  console.error('Unhandled rejection:', err);
  process.exit(1);
});
