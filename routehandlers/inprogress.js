class inProgress {
  constructor() {
    throw new Error('Use inProgress.getInstance()');
  }
  
  static getInstance() {
    if (!inProgress.instance) {
      inProgress.instance = new Map();
    }
    return inProgress.instance;
  }
}

module.exports = inProgress;
