import jakarta.persistence.*;
import java.io.Serializable;

@Entity
@Table(name = "ui_config")
public class UIConfig implements Serializable {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "config_name", unique = true, nullable = false)
    private String configName;

    @Column(name = "config_data", columnDefinition = "json")
    private String configData;

    // Getters and setters
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getConfigName() {
        return configName;
    }

    public void setConfigName(String configName) {
        this.configName = configName;
    }

    public String getConfigData() {
        return configData;
    }

    public void setConfigData(String configData) {
        this.configData = configData;
    }
}


--------------

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import com.fasterxml.jackson.core.JsonProcessingException;
import org.springframework.transaction.annotation.Transactional;

@Service
public class UIConfigService {
    @Autowired
    private UIConfigRepository uiConfigRepository;

    @Autowired
    private ObjectMapper objectMapper;

    public JsonNode getUIConfig() {
        UIConfig config = uiConfigRepository.findByConfigName("uiSettings")
            .orElseThrow(() -> new RuntimeException("UI config with name not found"));
        try {
            return objectMapper.readTree(config.getConfigData());
        } catch (JsonProcessingException e) {
            throw new RuntimeException("Error parsing JSON data", e);
        }
    }

    @Transactional
    public UIConfig createUIConfig(UIConfig uiConfig) {
        try {
            JsonNode jsonNode = objectMapper.readTree(uiConfig.getConfigData());
            String jsonString = objectMapper.writeValueAsString(jsonNode);
            uiConfig.setConfigData(jsonString);
            return uiConfigRepository.save(uiConfig);
        } catch (JsonProcessingException e) {
            throw new RuntimeException("Error processing JSON data", e);
        }
    }

    @Transactional
    public UIConfig updateUIConfig(Long id, UIConfig uiConfig) {
        UIConfig configToUpdate = uiConfigRepository.findById(id)
            .orElseThrow(() -> new RuntimeException("UI config with id " + id + " not found"));
        
        configToUpdate.setConfigName(uiConfig.getConfigName());
        try {
            JsonNode jsonNode = objectMapper.readTree(uiConfig.getConfigData());
            String jsonString = objectMapper.writeValueAsString(jsonNode);
            configToUpdate.setConfigData(jsonString);
            return uiConfigRepository.save(configToUpdate);
        } catch (JsonProcessingException e) {
            throw new RuntimeException("Error processing JSON data", e);
        }
    }

    public void deleteUIConfig(Long id) {
        uiConfigRepository.deleteById(id);
    }

    public boolean isFeatureEnabled(String featureName) {
        try {
            JsonNode configData = getUIConfig();
            JsonNode featureFlags = configData.path("featureFlags");
            return featureFlags.path(featureName).asBoolean(false);
        } catch (Exception e) {
            return false;
        }
    }
}


-------

import com.fasterxml.jackson.databind.JsonNode;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/ui-config")
public class UIConfigController {
    @Autowired
    private UIConfigService uiConfigService;

    @GetMapping("/ui-settings")
    public ResponseEntity<JsonNode> getUIConfig() {
        JsonNode config = uiConfigService.getUIConfig();
        return ResponseEntity.ok(config);
    }

    @PostMapping
    public ResponseEntity<UIConfig> createUIConfig(@RequestBody UIConfig uiConfig) {
        UIConfig createdConfig = uiConfigService.createUIConfig(uiConfig);
        return new ResponseEntity<>(createdConfig, HttpStatus.CREATED);
    }

    @PutMapping("/{id}")
    public ResponseEntity<UIConfig> updateUIConfig(@PathVariable Long id, @RequestBody UIConfig uiConfig) {
        UIConfig updatedConfig = uiConfigService.updateUIConfig(id, uiConfig);
        return ResponseEntity.ok(updatedConfig);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteUIConfig(@PathVariable Long id) {
        uiConfigService.deleteUIConfig(id);
        return ResponseEntity.noContent().build();
    }

    @GetMapping("/feature-enabled/{featureName}")
    public ResponseEntity<Boolean> isFeatureEnabled(@PathVariable String featureName) {
        boolean isEnabled = uiConfigService.isFeatureEnabled(featureName);
        return ResponseEntity.ok(isEnabled);
    }
}


------------
