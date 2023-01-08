#include "Pch.hpp"

#include "Application.hpp"

#include <SDL2/SDL.h>
#include <SDL2/SDL_syswm.h>

#include <DirectXTex.h>

namespace pcviz
{
    Application::Application(const std::string_view windowTitle) : m_windowTitle(windowTitle) {}

    Application::~Application() { cleanup(); }

    void Application::run()
    {
        try
        {
            init();

            loadContent();

            std::chrono::high_resolution_clock clock{};
            std::chrono::high_resolution_clock::time_point previousFrameTime{};

            bool quit = false;
            while (!quit)
            {
                SDL_Event event{};
                while (SDL_PollEvent(&event))
                {
                    ImGui_ImplSDL2_ProcessEvent(&event);

                    if (event.type == SDL_QUIT)
                    {
                        quit = true;
                    }

                    const uint8_t* keyboardState = SDL_GetKeyboardState(nullptr);
                    if (keyboardState[SDL_SCANCODE_ESCAPE])
                    {
                        quit = true;
                    }

                    m_camera.handleInput(Keys::W, keyboardState[SDL_SCANCODE_W]);
                    m_camera.handleInput(Keys::A, keyboardState[SDL_SCANCODE_A]);
                    m_camera.handleInput(Keys::S, keyboardState[SDL_SCANCODE_S]);
                    m_camera.handleInput(Keys::D, keyboardState[SDL_SCANCODE_D]);

                    m_camera.handleInput(Keys::AUp, keyboardState[SDL_SCANCODE_UP]);
                    m_camera.handleInput(Keys::ALeft, keyboardState[SDL_SCANCODE_LEFT]);
                    m_camera.handleInput(Keys::ADown, keyboardState[SDL_SCANCODE_DOWN]);
                    m_camera.handleInput(Keys::ARight, keyboardState[SDL_SCANCODE_RIGHT]);
                }

                const auto currentFrameTime = clock.now();
                const float deltaTime = static_cast<float>((currentFrameTime - previousFrameTime).count() * 1e-9);
                previousFrameTime = currentFrameTime;

                update(deltaTime);
                render();
            }
        }
        catch (const std::exception& exception)
        {
            std::cerr << exception.what() << "\n";
            return;
        }
    }

    void Application::init()
    {
        // Set DPI awareness on Windows
        SDL_SetHint(SDL_HINT_WINDOWS_DPI_AWARENESS, "permonitorv2");
        SDL_SetHint(SDL_HINT_WINDOWS_DPI_SCALING, "1");

        // Initialize SDL2 and create window.
        if (SDL_Init(SDL_INIT_EVERYTHING) < 0)
        {
            fatalError("Failed to initialize SDL2.");
        }

        // Get monitor dimensions.
        SDL_DisplayMode displayMode{};
        if (SDL_GetCurrentDisplayMode(0, &displayMode) < 0)
        {
            fatalError("Failed to get display mode.");
        }

        const uint32_t monitorWidth = displayMode.w;
        const uint32_t monitorHeight = displayMode.h;

        // Window must cover 100% of the screen.
        m_windowWidth = static_cast<uint32_t>(monitorWidth * 1.00f);
        m_windowHeight = static_cast<uint32_t>(monitorHeight * 1.00f);

        // Not made const as SDL_DestroyWindow requires us to pass a non - const SDL_Window.
        SDL_Window* m_window = SDL_CreateWindow("Point Cloud Visualizer", SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, m_windowWidth, m_windowHeight, SDL_WINDOW_ALLOW_HIGHDPI);

        if (!m_window)
        {
            fatalError("Failed to create SDL2 window.");
        }

        SDL_SysWMinfo wmInfo{};
        SDL_VERSION(&wmInfo.version);

        SDL_GetWindowWMInfo(m_window, &wmInfo);
        m_windowHandle = wmInfo.info.win.window;

        // Initialize graphics back end.
        createDeviceResources();
        createSwapchainResources();

        // Init Imgui.
        IMGUI_CHECKVERSION();
        ImGui::CreateContext();

        ImGui::StyleColorsDark();
        ImGui_ImplSDL2_InitForD3D(m_window);
        ImGui_ImplDX11_Init(m_device.Get(), m_deviceContext.Get());
    }

    void Application::cleanup()
    {

        ImGui_ImplDX11_Shutdown();
        ImGui_ImplSDL2_Shutdown();
        ImGui::DestroyContext();

        SDL_DestroyWindow(m_window);
        SDL_Quit();
    }

    void Application::createDeviceResources()
    {
        // Create the DXGI factory (with debug flags set in debug build).
        uint32_t factoryCreationFlags = 0u;
        if constexpr (PCVIZ_DEBUG)
        {
            factoryCreationFlags = DXGI_CREATE_FACTORY_DEBUG;
        }

        throwIfFailed(::CreateDXGIFactory2(factoryCreationFlags, IID_PPV_ARGS(&m_factory)));

        // Get the adapter with best performance.
        comptr<IDXGIAdapter1> adapter{};
        throwIfFailed(m_factory->EnumAdapterByGpuPreference(0u, DXGI_GPU_PREFERENCE_HIGH_PERFORMANCE, IID_PPV_ARGS(&adapter)));

        uint32_t deviceCreationFlags = 0u;

        if constexpr (PCVIZ_DEBUG)
        {
            deviceCreationFlags |= D3D11_CREATE_DEVICE_DEBUG;

            // Display chosen adapter.
            DXGI_ADAPTER_DESC1 adapterDesc{};
            throwIfFailed(adapter->GetDesc1(&adapterDesc));

            std::cout << "Chosen Adapter : ";
            std::wcout << adapterDesc.Description << L'\n';
        }

        // Create the D3D11 device and device context.
        throwIfFailed(
            ::D3D11CreateDevice(adapter.Get(), D3D_DRIVER_TYPE_UNKNOWN, nullptr, deviceCreationFlags, nullptr, 0u, D3D11_SDK_VERSION, &m_device, nullptr, &m_deviceContext));

        if constexpr (PCVIZ_DEBUG)
        {
            // Enable debug layer.
            throwIfFailed(m_device.As(&m_debug));

            // Setup info queue.
            throwIfFailed(m_device.As(&m_infoQueue));
            throwIfFailed(m_infoQueue->SetBreakOnSeverity(D3D11_MESSAGE_SEVERITY_CORRUPTION, true));
            throwIfFailed(m_infoQueue->SetBreakOnSeverity(D3D11_MESSAGE_SEVERITY_ERROR, true));
            throwIfFailed(m_infoQueue->SetBreakOnSeverity(D3D11_MESSAGE_SEVERITY_WARNING, true));
        }
    }

    void Application::createSwapchainResources()
    {
        // Create the swapchain.
        const DXGI_SWAP_CHAIN_DESC1 swapChainDesc = {
            .Width = m_windowWidth,
            .Height = m_windowHeight,
            .Format = DXGI_FORMAT_R10G10B10A2_UNORM,
            .SampleDesc = {1u, 0u},
            .BufferUsage = DXGI_USAGE_RENDER_TARGET_OUTPUT,
            .BufferCount = 2u,
            .Scaling = DXGI_SCALING_STRETCH,
            .SwapEffect = DXGI_SWAP_EFFECT_FLIP_DISCARD,
            .Flags = 0u,
        };

        throwIfFailed(m_factory->CreateSwapChainForHwnd(m_device.Get(), m_windowHandle, &swapChainDesc, nullptr, nullptr, &m_swapchain));

        // Setup the swapchain backbuffer render target view.
        comptr<ID3D11Texture2D> backBuffer{};
        throwIfFailed(m_swapchain->GetBuffer(0u, IID_PPV_ARGS(&backBuffer)));

        throwIfFailed(m_device->CreateRenderTargetView(backBuffer.Get(), nullptr, &m_renderTargetView));

        m_viewport = {
            .TopLeftX = 0.0f,
            .TopLeftY = 0.0f,
            .Width = static_cast<float>(m_windowWidth),
            .Height = static_cast<float>(m_windowHeight),
            .MinDepth = 0.0f,
            .MaxDepth = 1.0f,
        };
    }

    Microsoft::WRL::ComPtr<ID3D11VertexShader> Application::createVertexShader(const std::wstring_view shaderPath, comptr<ID3DBlob>& outShaderBlob)
    {
        comptr<ID3D11VertexShader> vertexShader{};

        comptr<ID3DBlob> errorBlob{};

        if (FAILED(::D3DCompileFromFile(shaderPath.data(), nullptr, nullptr, "VsMain", "vs_5_0", 0u, 0u, &outShaderBlob, &errorBlob)))
        {
            std::wcout << "Error in compiling shader : " << shaderPath << ". Error : " << static_cast<const char*>(errorBlob->GetBufferPointer());
            throw std::runtime_error("Shader compilation error.");
        }

        throwIfFailed(m_device->CreateVertexShader(outShaderBlob->GetBufferPointer(), outShaderBlob->GetBufferSize(), nullptr, &vertexShader));

        return vertexShader;
    }

    void Application::bindPipeline(const GraphicsPipeline& pipeline)
    {
        m_deviceContext->IASetPrimitiveTopology(pipeline.primitiveTopology);
        m_deviceContext->IASetInputLayout(pipeline.inputLayout.Get());

        m_deviceContext->VSSetShader(pipeline.vertexShader.Get(), nullptr, 0u);
        m_deviceContext->PSSetShader(pipeline.pixelShader.Get(), nullptr, 0u);
    }

    void Application::bindTexturePS(ID3D11ShaderResourceView* const srv, const uint32_t bindSlot) { m_deviceContext->PSSetShaderResources(bindSlot, 1u, &srv); }

    Microsoft::WRL::ComPtr<ID3D11PixelShader> Application::createPixelShader(const std::wstring_view shaderPath)
    {
        comptr<ID3D11PixelShader> pixelShader{};

        comptr<ID3DBlob> shaderBlob{};
        comptr<ID3DBlob> errorBlob{};

        if (FAILED(::D3DCompileFromFile(shaderPath.data(), nullptr, nullptr, "PsMain", "ps_5_0", 0u, 0u, &shaderBlob, &errorBlob)))
        {
            std::wcout << "Error in compiling shader : " << shaderPath << ". Error : " << static_cast<const char*>(errorBlob->GetBufferPointer());
            throw std::runtime_error("Shader compilation error.");
        }

        throwIfFailed(m_device->CreatePixelShader(shaderBlob->GetBufferPointer(), shaderBlob->GetBufferSize(), nullptr, &pixelShader));

        return pixelShader;
    }

    Microsoft::WRL::ComPtr<ID3D11InputLayout> Application::createInputLayout(ID3DBlob* vertexShaderBlob, std::span<const InputLayoutElementDesc> inputLayoutElementDescs)
    {
        if (inputLayoutElementDescs.size() == 0)
        {
            return nullptr;
        }

        comptr<ID3D11InputLayout> inputLayout{};

        std::vector<D3D11_INPUT_ELEMENT_DESC> inputElementDescs{};
        inputElementDescs.reserve(inputLayoutElementDescs.size());

        for (const auto& inputLayoutElementDesc : inputLayoutElementDescs)
        {
            inputElementDescs.emplace_back(D3D11_INPUT_ELEMENT_DESC{
                .SemanticName = inputLayoutElementDesc.semanticName.c_str(),
                .SemanticIndex = 0u,
                .Format = inputLayoutElementDesc.format,
                .InputSlot = 0u,
                .AlignedByteOffset = D3D11_APPEND_ALIGNED_ELEMENT,
                .InputSlotClass = inputLayoutElementDesc.inputClassification,
                .InstanceDataStepRate = 0u,
            });
        }

        throwIfFailed(m_device->CreateInputLayout(inputElementDescs.data(),
                                                  static_cast<uint32_t>(inputElementDescs.size()),
                                                  vertexShaderBlob->GetBufferPointer(),
                                                  vertexShaderBlob->GetBufferSize(),
                                                  &inputLayout));

        return inputLayout;
    }

    GraphicsPipeline Application::createGraphicsPipeline(const GraphicsPipelineCreationDesc& pipelineCreationDesc)
    {
        comptr<ID3DBlob> vertexShaderBlob{};

        comptr<ID3D11VertexShader> vertexShader = createVertexShader(pipelineCreationDesc.vertexShaderPath, vertexShaderBlob);

        return GraphicsPipeline{
            .vertexShader = vertexShader,
            .pixelShader = createPixelShader(pipelineCreationDesc.pixelShaderPath),
            .inputLayout = createInputLayout(vertexShaderBlob.Get(), pipelineCreationDesc.inputLayoutElements),
            .primitiveTopology = pipelineCreationDesc.primitiveTopology,
            .vertexSize = pipelineCreationDesc.vertexSize,
        };
    }

    wrl::ComPtr<ID3D11ShaderResourceView> Application::createTexture(const std::wstring_view texturePath)
    {
        // Main reference : https://github.com/GraphicsProgramming/learnd3d11/blob/main/src/Cpp/1-getting-started/1-3-1-Texturing/TexturingApplication.cpp.

        comptr<ID3D11ShaderResourceView> srv{};

        DirectX::TexMetadata metaData{};
        DirectX::ScratchImage scratchImage{};

        if (FAILED(DirectX::LoadFromWICFile(texturePath.data(), DirectX::WIC_FLAGS_NONE, &metaData, scratchImage)))
        {
            std::wcout << L"Failed to load texture from path : " << texturePath << L'\n';
            throw std::runtime_error("Texture Loading Error");
        }

        DirectX::ScratchImage mipChain{};
        throwIfFailed(DirectX::GenerateMipMaps(scratchImage.GetImages(), scratchImage.GetImageCount(), metaData, DirectX::TEX_FILTER_DEFAULT, 0u, mipChain));

        comptr<ID3D11Resource> texture{};
        throwIfFailed(DirectX::CreateTexture(m_device.Get(), mipChain.GetImages(), mipChain.GetImageCount(), mipChain.GetMetadata(), &texture));

        throwIfFailed(DirectX::CreateShaderResourceView(m_device.Get(), mipChain.GetImages(), mipChain.GetImageCount(), mipChain.GetMetadata(), &srv));

        return srv;
    }

    wrl::ComPtr<ID3D11SamplerState> Application::createSampler(const SamplerCreationDesc& samplerCreationDesc)
    {
        comptr<ID3D11SamplerState> sampler{};

        const D3D11_SAMPLER_DESC samplerDesc = {
            .Filter = samplerCreationDesc.filter,
            .AddressU = samplerCreationDesc.addressMode,
            .AddressV = samplerCreationDesc.addressMode,
            .AddressW = samplerCreationDesc.addressMode,
            .MaxAnisotropy = D3D11_MAX_MAXANISOTROPY,
            .ComparisonFunc = D3D11_COMPARISON_NEVER,
        };

        throwIfFailed(m_device->CreateSamplerState(&samplerDesc, &sampler));

        return sampler;
    }

    RenderTarget Application::createRenderTarget(const uint32_t width, const uint32_t height, const DXGI_FORMAT format)
    {
        RenderTarget renderTarget{};

        const D3D11_TEXTURE2D_DESC textureDesc = {
            .Width = width,
            .Height = height,
            .MipLevels = 1u,
            .ArraySize = 1u,
            .Format = format,
            .SampleDesc = {1u, 0u},
            .Usage = D3D11_USAGE_DEFAULT,
            .BindFlags = D3D11_BIND_RENDER_TARGET | D3D11_BIND_SHADER_RESOURCE,
            .CPUAccessFlags = 0u,
        };

        throwIfFailed(m_device->CreateTexture2D(&textureDesc, nullptr, &renderTarget.texture));

        const D3D11_RENDER_TARGET_VIEW_DESC rtvDesc = {
            .Format = format,
            .ViewDimension = D3D11_RTV_DIMENSION_TEXTURE2D,
            .Texture2D =
                {
                    .MipSlice = 0u,
                },
        };

        throwIfFailed(m_device->CreateRenderTargetView(renderTarget.texture.Get(), &rtvDesc, &renderTarget.rtv));

        const D3D11_SHADER_RESOURCE_VIEW_DESC srvDesc = {
            .Format = format,
            .ViewDimension = D3D11_SRV_DIMENSION_TEXTURE2D,
            .Texture2D =
                {
                    .MostDetailedMip = 0u,
                    .MipLevels = 1u,
                },
        };

        throwIfFailed(m_device->CreateShaderResourceView(renderTarget.texture.Get(), &srvDesc, &renderTarget.srv));

        return renderTarget;
    }

    DepthTexture Application::createDepthTexture()
    {
        DepthTexture depthTexture{};

        comptr<ID3D11Texture2D> depthBuffer{};

        const D3D11_TEXTURE2D_DESC depthStencilBufferDesc = {
            .Width = m_windowWidth,
            .Height = m_windowHeight,
            .MipLevels = 1u,
            .ArraySize = 1u,
            .Format = DXGI_FORMAT_R32_TYPELESS,
            .SampleDesc = {1u, 0u},
            .Usage = D3D11_USAGE_DEFAULT,
            .BindFlags = D3D11_BIND_DEPTH_STENCIL | D3D11_BIND_SHADER_RESOURCE,
        };

        const D3D11_DEPTH_STENCIL_VIEW_DESC dsvDesc = {
            .Format = DXGI_FORMAT_D32_FLOAT,
            .ViewDimension = D3D11_DSV_DIMENSION_TEXTURE2D,
            .Texture2D =
                {
                    .MipSlice = 0u,
                },
        };

        throwIfFailed(m_device->CreateTexture2D(&depthStencilBufferDesc, nullptr, &depthBuffer));
        throwIfFailed(m_device->CreateDepthStencilView(depthBuffer.Get(), &dsvDesc, &depthTexture.dsv));

        const D3D11_SHADER_RESOURCE_VIEW_DESC srvDesc = {
            .Format = DXGI_FORMAT_R32_FLOAT,
            .ViewDimension = D3D11_SRV_DIMENSION_TEXTURE2D,
            .Texture2D =
                {
                    .MostDetailedMip = 0u,
                    .MipLevels = 1u,
                },
        };

        throwIfFailed(m_device->CreateShaderResourceView(depthBuffer.Get(), &srvDesc, &depthTexture.srv));

        return depthTexture;
    }
}
