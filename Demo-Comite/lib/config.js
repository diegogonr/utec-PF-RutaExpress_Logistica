const fs = require("fs");
const path = require("path");
const { execSync } = require("child_process");

// MVP — valores fijos del despliegue (override opcional con process.env)
const MVP = {
  PORT: "3080",
  APIM_BASE_URL: "https://apim-rutaexpress-mvp.azure-api.net",
  APIM_SUBSCRIPTION_KEY: "62e8ffbadae742339bf0709737c3a717",
  AWS_ALB_BASE_URL: "http://rutaexpress-mvp-mobile-alb-208219070.us-east-1.elb.amazonaws.com",
  SERVICE_BUS_CONNECTION_STRING: "",
  AZURE_RESOURCE_GROUP: "rg_Diego_Gonzales",
  SERVICE_BUS_NAMESPACE: "sb-rutaexpress-mvp",
  SERVICE_BUS_QUEUE: "q-inventory",
};

try {
  require("dotenv").config({ path: path.join(__dirname, "..", ".env") });
} catch {
  /* dotenv opcional */
}

const localPath = path.join(__dirname, "..", "config.local.json");
if (fs.existsSync(localPath)) {
  Object.assign(process.env, JSON.parse(fs.readFileSync(localPath, "utf8")));
}

function get(name, fallback = "") {
  return (process.env[name] || MVP[name] || fallback).trim();
}

function getServiceBusConnectionString() {
  const direct = get("SERVICE_BUS_CONNECTION_STRING");
  if (direct) return direct;

  const rg = get("AZURE_RESOURCE_GROUP");
  const ns = get("SERVICE_BUS_NAMESPACE", "sb-rutaexpress-mvp");
  if (!rg) return "";

  try {
    return execSync(
      `az servicebus namespace authorization-rule keys list --resource-group ${rg} --namespace-name ${ns} --name RootManageSharedAccessKey --query primaryConnectionString -o tsv`,
      { encoding: "utf8", stdio: ["pipe", "pipe", "pipe"] }
    ).trim();
  } catch {
    return "";
  }
}

module.exports = {
  port: Number(get("PORT", "3080")),
  apimBaseUrl: get("APIM_BASE_URL", MVP.APIM_BASE_URL),
  apimKey: get("APIM_SUBSCRIPTION_KEY", MVP.APIM_SUBSCRIPTION_KEY),
  awsAlbBaseUrl: get("AWS_ALB_BASE_URL", MVP.AWS_ALB_BASE_URL),
  serviceBusQueue: get("SERVICE_BUS_QUEUE", MVP.SERVICE_BUS_QUEUE),
  getServiceBusConnectionString,
  status() {
    return {
      apim: Boolean(this.apimKey),
      aws: Boolean(this.awsAlbBaseUrl),
      serviceBus: Boolean(getServiceBusConnectionString()),
    };
  },
};
