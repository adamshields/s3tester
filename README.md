```
@PostMapping
public ResponseEntity<UIConfig> createUIConfig(@RequestBody String jsonBody) {
    try {
        JsonNode jsonNode = objectMapper.readTree(jsonBody);
        UIConfig uiConfig = new UIConfig();
        uiConfig.setConfigName(jsonNode.get("configName").asText());
        uiConfig.setConfigData(jsonNode.get("configData").toString());
        UIConfig createdConfig = uiConfigService.createUIConfig(uiConfig);
        return new ResponseEntity<>(createdConfig, HttpStatus.CREATED);
    } catch (JsonProcessingException e) {
        throw new RuntimeException("Error processing JSON data", e);
    }
}

@PutMapping("/{id}")
public ResponseEntity<UIConfig> updateUIConfig(@PathVariable Long id, @RequestBody String jsonBody) {
    try {
        JsonNode jsonNode = objectMapper.readTree(jsonBody);
        UIConfig uiConfig = new UIConfig();
        uiConfig.setConfigName(jsonNode.get("configName").asText());
        uiConfig.setConfigData(jsonNode.get("configData").toString());
        UIConfig updatedConfig = uiConfigService.updateUIConfig(id, uiConfig);
        return ResponseEntity.ok(updatedConfig);
    } catch (JsonProcessingException e) {
        throw new RuntimeException("Error processing JSON data", e);
    }
}




@Transactional
public UIConfig createUIConfig(UIConfig uiConfig) {
    return uiConfigRepository.save(uiConfig);
}

@Transactional
public UIConfig updateUIConfig(Long id, UIConfig uiConfig) {
    UIConfig configToUpdate = uiConfigRepository.findById(id)
        .orElseThrow(() -> new RuntimeException("UI config with id " + id + " not found"));
    
    configToUpdate.setConfigName(uiConfig.getConfigName());
    configToUpdate.setConfigData(uiConfig.getConfigData());
    return uiConfigRepository.save(configToUpdate);
}
------------
```
