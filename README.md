```
import os
import xml.etree.ElementTree as ET

# Define the base directory of the project
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
resources_dir = os.path.join(base_dir, 'src', 'main', 'resources')
changelog_dir = os.path.join(resources_dir, 'DATABASE', 'CHANGELOG')
table_dir = os.path.join(resources_dir, 'DATABASE', 'TABLE')
master_file = os.path.join(changelog_dir, 'master.xml')

# Register the namespace to avoid ns0 prefix
ET.register_namespace('', "http://www.liquibase.org/xml/ns/dbchangelog")

# Function to modify XML files
def modify_xml(file_path, base_id):
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        change_set_counter = 1
        for changeSet in root.findall('{http://www.liquibase.org/xml/ns/dbchangelog}changeSet'):
            new_id = f"{base_id}-{change_set_counter}"
            changeSet.set('id', new_id)
            print(f"Updating file: {file_path} | changeSet ID: {new_id}")
            change_set_counter += 1
        
        tree.write(file_path, encoding='utf-8', xml_declaration=True)
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")

# Read the master file to determine the order of included files
try:
    master_tree = ET.parse(master_file)
    master_root = master_tree.getroot()
except Exception as e:
    print(f"Error reading master file: {e}")
    exit(1)

file_counter = 1
for include in master_root.findall('{http://www.liquibase.org/xml/ns/dbchangelog}include'):
    relative_file_path = include.get('file')
    file_path = os.path.join(resources_dir, relative_file_path.replace('/', os.sep))
    base_id = f"1.0.0-{file_counter}"
    
    if os.path.exists(file_path):
        print(f"Processing file: {file_path} with base ID: {base_id}")
        modify_xml(file_path, base_id)
        file_counter += 1
    else:
        print(f"File not found: {file_path}")

print('All XML files have been modified.')

```

```
import javax.persistence.*;
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


----
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;

public interface UIConfigRepository extends JpaRepository<UIConfig, Long> {
    Optional<UIConfig> findByConfigName(String configName);
}

-----
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import com.fasterxml.jackson.core.JsonProcessingException;

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

    public UIConfig createUIConfig(UIConfig uiConfig) {
        try {
            String jsonString = objectMapper.writeValueAsString(uiConfig.getConfigData());
            uiConfig.setConfigData(jsonString);
            return uiConfigRepository.save(uiConfig);
        } catch (JsonProcessingException e) {
            throw new RuntimeException("Error converting JSON data", e);
        }
    }

    public UIConfig updateUIConfig(Long id, UIConfig uiConfig) {
        UIConfig configToUpdate = uiConfigRepository.findById(id)
            .orElseThrow(() -> new RuntimeException("UI config with id " + id + " not found"));
        
        configToUpdate.setConfigName(uiConfig.getConfigName());
        try {
            String jsonString = objectMapper.writeValueAsString(uiConfig.getConfigData());
            configToUpdate.setConfigData(jsonString);
            return uiConfigRepository.save(configToUpdate);
        } catch (JsonProcessingException e) {
            throw new RuntimeException("Error converting JSON data", e);
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
----
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
```
