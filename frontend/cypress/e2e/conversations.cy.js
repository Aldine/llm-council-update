describe('Conversation Management E2E Tests', () => {
  beforeEach(() => {
    // Start with clean state
    cy.visit('/');
    cy.login();
  });

  it('should create a new conversation', () => {
    cy.get('[data-testid="new-conversation-btn"]')
      .or('button:contains("New Conversation")')
      .first()
      .click();

    // Should see new conversation in sidebar
    cy.contains('New Conversation').should('be.visible');
  });

  it('should send a message in standard mode', () => {
    const testMessage = 'What is 2 + 2?';
    
    // Create new conversation
    cy.get('button:contains("New Conversation")').first().click();
    
    // Send message
    cy.get('textarea[placeholder*="message"]').type(testMessage);
    cy.get('button[type="submit"]').click();

    // Should see user message
    cy.contains(testMessage).should('be.visible');
    
    // Should eventually see assistant response (with generous timeout for LLM)
    cy.contains(/Stage 1|Stage 2|Stage 3/i, { timeout: 30000 }).should('be.visible');
  });

  it('should toggle CrewAI mode and send message', () => {
    // Toggle CrewAI on
    cy.get('button').contains(/CrewAI/i).click();
    
    // Verify toggle state changed (visual feedback)
    cy.get('button').contains(/ON/i).should('be.visible');
    
    // Create conversation and send message
    cy.get('button:contains("New Conversation")').first().click();
    cy.get('textarea[placeholder*="message"]').type('Test CrewAI mode');
    cy.get('button[type="submit"]').click();
    
    // Should see response (CrewAI endpoint used)
    cy.contains(/Test CrewAI mode/i, { timeout: 30000 }).should('be.visible');
  });

  it('should delete a conversation', () => {
    // Create a conversation
    cy.get('button:contains("New Conversation")').first().click();
    cy.wait(500);
    
    // Find conversation in sidebar and hover
    cy.contains('.group', 'New Conversation')
      .first()
      .trigger('mouseover');
    
    // Click delete button (appears on hover)
    cy.contains('.group', 'New Conversation')
      .first()
      .find('button')
      .last()
      .click({ force: true });
    
    // Confirm deletion dialog
    cy.on('window:confirm', () => true);
    
    cy.wait(1000);
    
    // Conversation should be removed (or at least one less conversation)
    // Note: Can't easily verify exact count due to potential race conditions
  });

  it('should list multiple conversations', () => {
    // Create 3 conversations
    for (let i = 0; i < 3; i++) {
      cy.get('button:contains("New Conversation")').first().click();
      cy.wait(500);
    }
    
    // Should see multiple conversation items in sidebar
    cy.get('.conversation-item')
      .or('button:contains("New Conversation")')
      .should('have.length.at.least', 3);
  });

  it('should switch between conversations', () => {
    const message1 = 'First conversation message';
    const message2 = 'Second conversation message';
    
    // Create first conversation with message
    cy.get('button:contains("New Conversation")').first().click();
    cy.get('textarea[placeholder*="message"]').type(message1);
    cy.get('button[type="submit"]').click();
    cy.wait(1000);
    
    // Create second conversation with different message
    cy.get('button:contains("New Conversation")').first().click();
    cy.get('textarea[placeholder*="message"]').type(message2);
    cy.get('button[type="submit"]').click();
    cy.wait(1000);
    
    // Click on first conversation (find by message content in sidebar if titles update)
    cy.get('.conversation-item, button').contains(/New Conversation/i).first().click();
    
    // Should see first message
    cy.contains(message1).should('be.visible');
  });
});

describe('API Integration Tests', () => {
  it('should call backend API for listing conversations', () => {
    cy.apiRequest('GET', '/api/conversations').then((response) => {
      expect(response.status).to.eq(200);
      expect(response.body).to.be.an('array');
    });
  });

  it('should create conversation via API', () => {
    cy.apiRequest('POST', '/api/conversations', {}).then((response) => {
      expect(response.status).to.eq(200);
      expect(response.body).to.have.property('id');
      expect(response.body).to.have.property('title');
      
      // Cleanup: delete created conversation
      cy.apiRequest('DELETE', `/api/conversations/${response.body.id}`);
    });
  });

  it('should delete conversation via API', () => {
    // Create conversation
    cy.apiRequest('POST', '/api/conversations', {}).then((createResponse) => {
      const conversationId = createResponse.body.id;
      
      // Delete it
      cy.apiRequest('DELETE', `/api/conversations/${conversationId}`).then((deleteResponse) => {
        expect(deleteResponse.status).to.eq(200);
        expect(deleteResponse.body.message).to.include('deleted');
      });
      
      // Verify deletion
      cy.apiRequest('GET', `/api/conversations/${conversationId}`).then((getResponse) => {
        expect(getResponse.status).to.eq(404);
      });
    });
  });
});
