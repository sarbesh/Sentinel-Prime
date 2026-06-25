describe('SENTINEL PRIME Backend API Tests', () => {
  const baseUrl = 'http://localhost:8000';

  it('should return healthy status', () => {
    cy.request(`${baseUrl}/health`).then((response) => {
      expect(response.status).to.eq(200);
      expect(response.body).to.have.property('status', 'healthy');
    });
  });

  it('should return welcome message', () => {
    cy.request(`${baseUrl}/`).then((response) => {
      expect(response.status).to.eq(200);
      expect(response.body).to.have.property('message')
        .that.includes('SENTINEL PRIME Backend is running');
    });
  });
});

describe('MCP Endpoint Tests', () => {
  const baseUrl = 'http://localhost:8000';

  it('should return MCP health status', () => {
    cy.request(`${baseUrl}/mcp/health`).then((response) => {
      expect(response.status).to.eq(200);
      expect(response.body).to.have.property('status', 'healthy')
        .and.have.property('service', 'mcp');
    });
  });

  it('should return agent information', () => {
    cy.request(`${baseUrl}/mcp/agent`).then((response) => {
      expect(response.status).to.eq(200);
      expect(response.body).to.have.property('agent_id')
        .and.have.property('name')
        .and.have.property('capabilities')
        .that.is.an('array');
    });
  });

  it('should accept and return a task', () => {
    const taskData = {
      task_id: 'e2e_test_task_123',
      description: 'Test E2E task for MCP validation',
      parameters: {}
    };

    cy.request({
      method: 'POST',
      url: `${baseUrl}/mcp/task`,
      body: taskData,
      failOnStatusCode: false
    }).then((response) => {
      expect(response.status).to.be.oneOf([200, 201]);
      
      if (response.status === 200 || response.status === 201) {
        expect(response.body).to.have.property('taskId')
          .that.is.a('string');
        
        cy.request(`${baseUrl}/mcp/task/${response.body.taskId}`).then((taskResponse) => {
          expect(taskResponse.status).to.eq(200);
          expect(taskResponse.body).to.have.property('taskId')
            .eq(response.body.taskId);
        });
      }
    });
  });
});
EOF
