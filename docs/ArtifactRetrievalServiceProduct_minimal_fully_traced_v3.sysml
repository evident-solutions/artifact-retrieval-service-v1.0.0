package ArtifactRetrievalServiceProduct {

  attribute def Text;
  attribute def Flag;

  package DomainDefinitions {

    item def ArtifactDescriptor {
      attribute repository : Text;
      attribute artifactPath : Text;
      attribute versionSelector : Text;
    }

    item def TraceableArtifact {
      attribute artifactId : Text;
      attribute mimeType : Text[0..1];
    }

    port def AgentApiPort {
      in item request : ArtifactDescriptor;
      out item artifact : TraceableArtifact;
    }

    port def GitLabPort {
      out item request : ArtifactDescriptor;
      in item artifact : TraceableArtifact;
    }

    part def GitLabServer {
      attribute baseUrl : Text;
    }

    part def ApiGatewayComponent;
    part def RequestValidationComponent;
    part def RequestMappingComponent;

    part def ApiSubsystem {
      part gateway : ApiGatewayComponent;
      part validator : RequestValidationComponent;
      part mapper : RequestMappingComponent;
    }

    part def GitLabClientComponent;
    part def GitLabAuthComponent;

    part def GitLabSubsystem {
      part client : GitLabClientComponent;
      part auth : GitLabAuthComponent;
    }

    part def LoggingComponent;
    part def HealthCheckComponent;

    part def MonitoringSubsystem {
      part logger : LoggingComponent;
      part health : HealthCheckComponent;
    }

    part def ArtifactRetrievalService {

      attribute name : Text;

      port agentApi : AgentApiPort;
      port gitLabApi : GitLabPort;

      ref part gitLab : GitLabServer;

      part apiSubsystem : ApiSubsystem;
      part gitLabSubsystem : GitLabSubsystem;
      part monitoringSubsystem : MonitoringSubsystem;
    }

  }

  package UseCaseModel {

    use case 'retrieve artifact' {
      doc
      /*
       * UC-ARS-01
       * AI agent requests an artifact for downstream reasoning.
       */
      subject service : DomainDefinitions::ArtifactRetrievalService;
    }

    use case 'monitor service' {
      doc
      /*
       * UC-ARS-02
       * Operators or agents monitor health and logs.
       */
      subject service : DomainDefinitions::ArtifactRetrievalService;
    }
  }

  package RequirementsModel {

    requirement def ARS_CoreRetrieval {
      doc
      /*
       * ARS-SR-001
       * The service shall retrieve artifacts from GitLab given a descriptor.
       */
      attribute id : Text;
      attribute description : Text;
      attribute rationale : Text[0..1];
      attribute source : Text[0..1];
      attribute owner : Text[0..1];
      attribute verificationMethod : Text[0..1];
      attribute priority : Text[0..1];
      attribute risk : Text[0..1];
      attribute derivedFromId : Text[0..*];
      attribute derivedById : Text[0..*];
    }

    requirement def ARS_AgentApiContract {
      doc
      /*
       * ARS-SR-002
       * The service shall expose a stable agent API using ArtifactDescriptor
       * as input and TraceableArtifact as output.
       */
      attribute id : Text;
      attribute description : Text;
      attribute rationale : Text[0..1];
      attribute source : Text[0..1];
      attribute owner : Text[0..1];
      attribute verificationMethod : Text[0..1];
      attribute priority : Text[0..1];
      attribute risk : Text[0..1];
      attribute derivedFromId : Text[0..*];
      attribute derivedById : Text[0..*];
    }

    requirement def ARS_ReliabilityMonitoring {
      doc
      /*
       * ARS-SR-003
       * The service shall provide monitoring of reliability-related events,
       * including logging and health reporting.
       */
      attribute id : Text;
      attribute description : Text;
      attribute rationale : Text[0..1];
      attribute source : Text[0..1];
      attribute owner : Text[0..1];
      attribute verificationMethod : Text[0..1];
      attribute priority : Text[0..1];
      attribute risk : Text[0..1];
      attribute derivedFromId : Text[0..*];
      attribute derivedById : Text[0..*];
    }

    requirement def ARS_API_ReceiveAndMap {
      doc
      /*
       * ARS-API-001
       * The API subsystem shall receive agent requests and map them into
       * ArtifactDescriptor structures for retrieval.
       */
      attribute id : Text;
      attribute description : Text;
      attribute rationale : Text[0..1];
      attribute source : Text[0..1];
      attribute owner : Text[0..1];
      attribute verificationMethod : Text[0..1];
      attribute priority : Text[0..1];
      attribute risk : Text[0..1];
      attribute derivedFromId : Text[0..*];
      attribute derivedById : Text[0..*];
    }

    requirement def ARS_API_AgentContract {
      doc
      /*
       * ARS-API-002
       * The API subsystem shall maintain request and response formats
       * consistent with the agent API contract.
       */
      attribute id : Text;
      attribute description : Text;
      attribute rationale : Text[0..1];
      attribute source : Text[0..1];
      attribute owner : Text[0..1];
      attribute verificationMethod : Text[0..1];
      attribute priority : Text[0..1];
      attribute risk : Text[0..1];
      attribute derivedFromId : Text[0..*];
      attribute derivedById : Text[0..*];
    }

    requirement def ARS_GitLab_Retrieve {
      doc
      /*
       * ARS-GL-001
       * The GitLab subsystem shall retrieve the specified artifact
       * from GitLab using the provided descriptor.
       */
      attribute id : Text;
      attribute description : Text;
      attribute rationale : Text[0..1];
      attribute source : Text[0..1];
      attribute owner : Text[0..1];
      attribute verificationMethod : Text[0..1];
      attribute priority : Text[0..1];
      attribute risk : Text[0..1];
      attribute derivedFromId : Text[0..*];
      attribute derivedById : Text[0..*];
    }

    requirement def ARS_Mon_LogAndHealth {
      doc
      /*
       * ARS-MON-001
       * The monitoring subsystem shall log significant events and
       * report health status for the service.
       */
      attribute id : Text;
      attribute description : Text;
      attribute rationale : Text[0..1];
      attribute source : Text[0..1];
      attribute owner : Text[0..1];
      attribute verificationMethod : Text[0..1];
      attribute priority : Text[0..1];
      attribute risk : Text[0..1];
      attribute derivedFromId : Text[0..*];
      attribute derivedById : Text[0..*];
    }

    requirement def ARS_API_Gateway_Route {
      doc
      /*
       * ARS-API-GW-001
       * The API gateway shall route incoming agent requests to the
       * internal API subsystem without loss or duplication.
       */
      attribute id : Text;
      attribute description : Text;
      attribute rationale : Text[0..1];
      attribute source : Text[0..1];
      attribute owner : Text[0..1];
      attribute verificationMethod : Text[0..1];
      attribute priority : Text[0..1];
      attribute risk : Text[0..1];
      attribute derivedFromId : Text[0..*];
      attribute derivedById : Text[0..*];
    }

    requirement def ARS_API_Validator_Check {
      doc
      /*
       * ARS-API-VAL-001
       * The request validation component shall check authentication,
       * required fields, and structure of agent requests.
       */
      attribute id : Text;
      attribute description : Text;
      attribute rationale : Text[0..1];
      attribute source : Text[0..1];
      attribute owner : Text[0..1];
      attribute verificationMethod : Text[0..1];
      attribute priority : Text[0..1];
      attribute risk : Text[0..1];
      attribute derivedFromId : Text[0..*];
      attribute derivedById : Text[0..*];
    }

    requirement def ARS_API_Mapper_BuildDescriptor {
      doc
      /*
       * ARS-API-MAP-001
       * The mapping component shall build complete ArtifactDescriptor
       * instances from validated requests.
       */
      attribute id : Text;
      attribute description : Text;
      attribute rationale : Text[0..1];
      attribute source : Text[0..1];
      attribute owner : Text[0..1];
      attribute verificationMethod : Text[0..1];
      attribute priority : Text[0..1];
      attribute risk : Text[0..1];
      attribute derivedFromId : Text[0..*];
      attribute derivedById : Text[0..*];
    }

    requirement def ARS_API_Interface_Contract_Enforced {
      doc
      /*
       * ARS-API-IFACE-001
       * The API subsystem shall enforce the agent API contract across
       * all exposed operations.
       */
      attribute id : Text;
      attribute description : Text;
      attribute rationale : Text[0..1];
      attribute source : Text[0..1];
      attribute owner : Text[0..1];
      attribute verificationMethod : Text[0..1];
      attribute priority : Text[0..1];
      attribute risk : Text[0..1];
      attribute derivedFromId : Text[0..*];
      attribute derivedById : Text[0..*];
    }

    requirement def ARS_GL_Client_Call {
      doc
      /*
       * ARS-GL-CLI-001
       * The GitLab client component shall perform the HTTP call to
       * retrieve artifact content and metadata.
       */
      attribute id : Text;
      attribute description : Text;
      attribute rationale : Text[0..1];
      attribute source : Text[0..1];
      attribute owner : Text[0..1];
      attribute verificationMethod : Text[0..1];
      attribute priority : Text[0..1];
      attribute risk : Text[0..1];
      attribute derivedFromId : Text[0..*];
      attribute derivedById : Text[0..*];
    }

    requirement def ARS_GL_Auth_Protect {
      doc
      /*
       * ARS-GL-AUTH-001
       * The GitLab auth component shall protect credentials and ensure
       * they are used only for authorized GitLab requests.
       */
      attribute id : Text;
      attribute description : Text;
      attribute rationale : Text[0..1];
      attribute source : Text[0..1];
      attribute owner : Text[0..1];
      attribute verificationMethod : Text[0..1];
      attribute priority : Text[0..1];
      attribute risk : Text[0..1];
      attribute derivedFromId : Text[0..*];
      attribute derivedById : Text[0..*];
    }

    requirement def ARS_MON_Logger_Record {
      doc
      /*
       * ARS-MON-LOG-001
       * The logging component shall record time-stamped events for
       * critical operations and failures.
       */
      attribute id : Text;
      attribute description : Text;
      attribute rationale : Text[0..1];
      attribute source : Text[0..1];
      attribute owner : Text[0..1];
      attribute verificationMethod : Text[0..1];
      attribute priority : Text[0..1];
      attribute risk : Text[0..1];
      attribute derivedFromId : Text[0..*];
      attribute derivedById : Text[0..*];
    }

    requirement def ARS_MON_Health_Report {
      doc
      /*
       * ARS-MON-HLT-001
       * The health component shall report readiness and liveness for
       * the service.
       */
      attribute id : Text;
      attribute description : Text;
      attribute rationale : Text[0..1];
      attribute source : Text[0..1];
      attribute owner : Text[0..1];
      attribute verificationMethod : Text[0..1];
      attribute priority : Text[0..1];
      attribute risk : Text[0..1];
      attribute derivedFromId : Text[0..*];
      attribute derivedById : Text[0..*];
    }

    requirement <'ARS-SR-001'> ARS_CoreRetrieval_req : ARS_CoreRetrieval;
    requirement <'ARS-SR-002'> ARS_AgentApiContract_req : ARS_AgentApiContract;
    requirement <'ARS-SR-003'> ARS_ReliabilityMonitoring_req : ARS_ReliabilityMonitoring;

    requirement <'ARS-API-001'> ARS_API_ReceiveAndMap_req : ARS_API_ReceiveAndMap;
    requirement <'ARS-API-002'> ARS_API_AgentContract_req : ARS_API_AgentContract;
    requirement <'ARS-GL-001'> ARS_GitLab_Retrieve_req : ARS_GitLab_Retrieve;
    requirement <'ARS-MON-001'> ARS_Mon_LogAndHealth_req : ARS_Mon_LogAndHealth;

    requirement <'ARS-API-GW-001'> ARS_API_Gateway_Route_req : ARS_API_Gateway_Route;
    requirement <'ARS-API-VAL-001'> ARS_API_Validator_Check_req : ARS_API_Validator_Check;
    requirement <'ARS-API-MAP-001'> ARS_API_Mapper_BuildDescriptor_req : ARS_API_Mapper_BuildDescriptor;
    requirement <'ARS-API-IFACE-001'> ARS_API_Interface_Contract_Enforced_req : ARS_API_Interface_Contract_Enforced;

    requirement <'ARS-GL-CLI-001'> ARS_GL_Client_Call_req : ARS_GL_Client_Call;
    requirement <'ARS-GL-AUTH-001'> ARS_GL_Auth_Protect_req : ARS_GL_Auth_Protect;

    requirement <'ARS-MON-LOG-001'> ARS_MON_Logger_Record_req : ARS_MON_Logger_Record;
    requirement <'ARS-MON-HLT-001'> ARS_MON_Health_Report_req : ARS_MON_Health_Report;

    requirement 'ARS CoreRetrieval Derivation' {
      require ARS_CoreRetrieval_req;
      require ARS_API_ReceiveAndMap_req;
      require ARS_GitLab_Retrieve_req;
    }

    requirement 'ARS AgentApi Derivation' {
      require ARS_AgentApiContract_req;
      require ARS_API_AgentContract_req;
    }

    requirement 'ARS ReliabilityMonitoring Derivation' {
      require ARS_ReliabilityMonitoring_req;
      require ARS_Mon_LogAndHealth_req;
    }

    requirement 'ARS API Subsystem Derivation' {
      require ARS_API_ReceiveAndMap_req;
      require ARS_API_Gateway_Route_req;
      require ARS_API_Validator_Check_req;
      require ARS_API_Mapper_BuildDescriptor_req;

      require ARS_API_AgentContract_req;
      require ARS_API_Interface_Contract_Enforced_req;
    }

    requirement 'ARS GitLab Subsystem Derivation' {
      require ARS_GitLab_Retrieve_req;
      require ARS_GL_Client_Call_req;
      require ARS_GL_Auth_Protect_req;
    }

    requirement 'ARS Monitoring Subsystem Derivation' {
      require ARS_Mon_LogAndHealth_req;
      require ARS_MON_Logger_Record_req;
      require ARS_MON_Health_Report_req;
    }

  }

  part artifactRetrievalServiceInstance :
    DomainDefinitions::ArtifactRetrievalService {

    attribute name : Text;

    part apiSubsystem : DomainDefinitions::ApiSubsystem {

      part gateway : DomainDefinitions::ApiGatewayComponent {
        satisfy RequirementsModel::ARS_API_Gateway_Route_req;
      }

      part validator : DomainDefinitions::RequestValidationComponent {
        satisfy RequirementsModel::ARS_API_Validator_Check_req;
      }

      part mapper : DomainDefinitions::RequestMappingComponent {
        satisfy RequirementsModel::ARS_API_Mapper_BuildDescriptor_req;
      }

      satisfy RequirementsModel::ARS_API_ReceiveAndMap_req;
      satisfy RequirementsModel::ARS_API_AgentContract_req;
      satisfy RequirementsModel::ARS_API_Interface_Contract_Enforced_req;
    }

    part gitLabSubsystem : DomainDefinitions::GitLabSubsystem {

      part client : DomainDefinitions::GitLabClientComponent {
        satisfy RequirementsModel::ARS_GL_Client_Call_req;
      }

      part auth : DomainDefinitions::GitLabAuthComponent {
        satisfy RequirementsModel::ARS_GL_Auth_Protect_req;
      }

      satisfy RequirementsModel::ARS_GitLab_Retrieve_req;
    }

    part monitoringSubsystem : DomainDefinitions::MonitoringSubsystem {

      part logger : DomainDefinitions::LoggingComponent {
        satisfy RequirementsModel::ARS_MON_Logger_Record_req;
      }

      part health : DomainDefinitions::HealthCheckComponent {
        satisfy RequirementsModel::ARS_MON_Health_Report_req;
      }

      satisfy RequirementsModel::ARS_Mon_LogAndHealth_req;
    }

    satisfy RequirementsModel::ARS_CoreRetrieval_req;
    satisfy RequirementsModel::ARS_AgentApiContract_req;
    satisfy RequirementsModel::ARS_ReliabilityMonitoring_req;
  }

}