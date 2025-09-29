import * as fs from 'fs';
import * as path from 'path';

describe('HTML模板单元测试', () => {
  const templatePath = path.join(__dirname, '../../../static/html/webview-template.html');

  describe('HTML模板文件完整性测试', () => {
    it('should have complete HTML structure', () => {
      // 读取HTML模板文件
      const templateContent = fs.readFileSync(templatePath, 'utf8');
      
      // 验证HTML文档结构完整性
      expect(templateContent).toContain('<!DOCTYPE html>');
      expect(templateContent).toContain('<html');
      expect(templateContent).toContain('</html>');
      expect(templateContent).toContain('<head');
      expect(templateContent).toContain('</head>');
      expect(templateContent).toContain('<body');
      expect(templateContent).toContain('</body>');
    });

    it('should have required meta tags', () => {
      const templateContent = fs.readFileSync(templatePath, 'utf8');
      
      expect(templateContent).toContain('<meta charset="UTF-8">');
      expect(templateContent).toContain('<meta name="viewport" content="width=device-width, initial-scale=1.0">');
    });

    it('should have valid title', () => {
      const templateContent = fs.readFileSync(templatePath, 'utf8');
      expect(templateContent).toContain('<title>Interactive Tool</title>');
    });
  });

  describe('模板占位符验证测试', () => {
    it('should contain all required placeholders', () => {
      const templateContent = fs.readFileSync(templatePath, 'utf8');
      
      // 验证所有必需的占位符
      expect(templateContent).toContain('{{vueJsPath}}');
      expect(templateContent).toContain('{{vueI18nJsPath}}');
      expect(templateContent).toContain('{{appJsPath}}');
      expect(templateContent).toContain('{{styleCssPath}}');
    });

    it('should have correct placeholder format', () => {
      const templateContent = fs.readFileSync(templatePath, 'utf8');
      
      // 检查占位符格式是否正确（双花括号）
      const placeholderRegex = /{{\s*\w+\s*}}/g;
      const matches = templateContent.match(placeholderRegex);
      
      expect(matches).toBeDefined();
      expect(matches!.length).toBeGreaterThanOrEqual(4);
    });
  });

  describe('模板渲染测试（脱离VSCode环境）', () => {
    it('should render HTML correctly with replaced placeholders', () => {
      const templateContent = fs.readFileSync(templatePath, 'utf8');
      
      // 替换占位符为测试路径
      const renderedHtml = templateContent
        .replace('{{vueJsPath}}', '/test/vue.min.js')
        .replace('{{vueI18nJsPath}}', '/test/vue-i18n.min.js')
        .replace('{{appJsPath}}', '/test/app.js')
        .replace('{{styleCssPath}}', '/test/style.css');
      
      // 验证占位符被正确替换
      expect(renderedHtml).not.toContain('{{vueJsPath}}');
      expect(renderedHtml).not.toContain('{{vueI18nJsPath}}');
      expect(renderedHtml).not.toContain('{{appJsPath}}');
      expect(renderedHtml).not.toContain('{{styleCssPath}}');
      
      // 验证替换后的路径是否正确
      expect(renderedHtml).toContain('/test/vue.min.js');
      expect(renderedHtml).toContain('/test/vue-i18n.min.js');
      expect(renderedHtml).toContain('/test/app.js');
      expect(renderedHtml).toContain('/test/style.css');
    });

    it('should maintain valid HTML structure after rendering', () => {
      const templateContent = fs.readFileSync(templatePath, 'utf8');
      
      const renderedHtml = templateContent
        .replace('{{vueJsPath}}', '/test/vue.min.js')
        .replace('{{vueI18nJsPath}}', '/test/vue-i18n.min.js')
        .replace('{{appJsPath}}', '/test/app.js')
        .replace('{{styleCssPath}}', '/test/style.css');
      
      // 验证渲染后的HTML结构仍然完整
      expect(renderedHtml).toContain('<!DOCTYPE html>');
      expect(renderedHtml).toContain('<html');
      expect(renderedHtml).toContain('<body');
      expect(renderedHtml).toContain('<div id="app">');
    });
  });

  describe('Vue应用结构验证', () => {
    it('should have correct Vue app structure', () => {
      const templateContent = fs.readFileSync(templatePath, 'utf8');
      
      // 验证Vue应用的基本结构
      expect(templateContent).toContain('<div id="app">');
      expect(templateContent).toContain('<div class="container">');
      expect(templateContent).toContain('<input v-model="inputData"');
      expect(templateContent).toContain('<button @click="sendCommand"');
      expect(templateContent).toContain('<div v-if="result" class="result">');
    });

    it('should include Vue i18n support', () => {
      const templateContent = fs.readFileSync(templatePath, 'utf8');
      
      // 验证包含国际化支持
      expect(templateContent).toContain('{{ $t(');
      expect(templateContent).toContain('{{ $t(\'welcome.title\') }}');
      expect(templateContent).toContain('{{ $t(\'input.placeholder\') }}');
      expect(templateContent).toContain('{{ $t(\'button.send\') }}');
    });
  });
});