// ***********************************************
// Custom commands for LLM Council E2E tests
// ***********************************************

/**
 * Login command for authentication
 */
Cypress.Commands.add('login', (email = 'demo@llmcouncil.com', password = 'demo123') => {
  cy.visit('/');
  
  // Check if already logged in
  cy.get('body').then(($body) => {
    if ($body.find('[data-testid="chat-interface"]').length === 0) {
      // Not logged in, perform login
      cy.get('input[type="email"]').type(email);
      cy.get('input[type="password"]').type(password);
      cy.get('button[type="submit"]').click();
      cy.wait(1000); // Wait for auth to complete
    }
  });
});

/**
 * Create a new conversation
 */
Cypress.Commands.add('createConversation', () => {
  cy.get('[data-testid="new-conversation-btn"]').click();
  cy.wait(500);
});

/**
 * Send a message in the current conversation
 */
Cypress.Commands.add('sendMessage', (message) => {
  cy.get('textarea[placeholder*="message"]').type(message);
  cy.get('button[type="submit"]').click();
});

/**
 * Delete a conversation by title
 */
Cypress.Commands.add('deleteConversation', (title) => {
  cy.contains('.conversation-item', title)
    .trigger('mouseover')
    .find('button[aria-label*="delete"]')
    .click({ force: true });
  
  // Confirm deletion
  cy.on('window:confirm', () => true);
});

/**
 * Toggle CrewAI mode
 */
Cypress.Commands.add('toggleCrewAI', () => {
  cy.get('[data-testid="crewai-toggle"]').click();
});

/**
 * API request helper
 */
Cypress.Commands.add('apiRequest', (method, endpoint, body = null) => {
  const token = localStorage.getItem('auth_access_token');
  
  return cy.request({
    method,
    url: `${Cypress.env('apiUrl')}${endpoint}`,
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
    },
    ...(body && { body }),
    failOnStatusCode: false,
  });
});
